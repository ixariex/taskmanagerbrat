from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.category_manager import (
    create_category,
    edit_category,
    get_category,
    remove_category,
)
from ui.category_dialog import CategoryDialog
from ui.silent_message_box import SilentMessageBox as QMessageBox
from ui.styles import PAGE_COMMON_STYLESHEET


class CategoriesWidget(QWidget):
    categoriesChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("categoriesPage")
        self.setStyleSheet(PAGE_COMMON_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        header = QVBoxLayout()
        header.setSpacing(4)
        eyebrow = QLabel("TASKFORGE / ORGANIZATION")
        eyebrow.setObjectName("pageEyebrow")
        title = QLabel("Categories")
        title.setObjectName("heroTitle")
        subtitle = QLabel("Organize your tasks and keep everything structured.")
        subtitle.setObjectName("heroSubtitle")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        panel = QFrame()
        panel.setObjectName("contentPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 15, 16, 15)
        panel_layout.setSpacing(13)

        panel_header = QHBoxLayout()
        section_title = QLabel("Your Categories")
        section_title.setObjectName("sectionTitle")
        self.category_count_label = QLabel("0 categories")
        self.category_count_label.setObjectName("countBadge")
        panel_header.addWidget(section_title)
        panel_header.addStretch()
        panel_header.addWidget(self.category_count_label)
        panel_layout.addLayout(panel_header)

        actions = QHBoxLayout()
        actions.setSpacing(9)

        add_button = QPushButton("+ Add Category")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(self.open_add_category)

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("secondaryButton")
        edit_button.clicked.connect(lambda: self.edit_selected_category())

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self.delete_selected_category)

        actions.addWidget(add_button)
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()
        panel_layout.addLayout(actions)

        self.categories_list = QListWidget()
        self.categories_list.setObjectName("cardList")
        self.categories_list.setSpacing(4)
        self.categories_list.itemDoubleClicked.connect(self.edit_selected_category)
        panel_layout.addWidget(self.categories_list, 1)

        layout.addWidget(panel, 1)

    def refresh_data(self, categories: list) -> None:
        self.categories_list.clear()
        self.category_count_label.setText(
            f"{len(categories)} categor{'y' if len(categories) == 1 else 'ies'}"
        )
        for category in categories:
            item = QListWidgetItem(f"{category[1]}   ({category[2]})")
            item.setData(Qt.ItemDataRole.UserRole, category[0])
            item.setForeground(QBrush(QColor(category[2])))
            self.categories_list.addItem(item)

    def open_add_category(self) -> None:
        dialog = CategoryDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            if not create_category(**dialog.get_data()):
                QMessageBox.warning(self, "Duplicate Category", "A category with this name already exists.")
                return
            self.categoriesChanged.emit()
        except Exception as error:
            QMessageBox.critical(self, "Category Error", str(error))

    def edit_selected_category(self, item: QListWidgetItem | None = None) -> None:
        if not isinstance(item, QListWidgetItem):
            item = self.categories_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a category first.")
            return
        category_id = item.data(Qt.ItemDataRole.UserRole)
        category = get_category(int(category_id))
        if category is None:
            QMessageBox.warning(self, "Not Found", "Category does not exist.")
            self.categoriesChanged.emit()
            return
        dialog = CategoryDialog(self, category=category)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            if not edit_category(int(category_id), **dialog.get_data()):
                QMessageBox.warning(self, "Update Failed", "Name may already be in use.")
                return
            self.categoriesChanged.emit()
        except Exception as error:
            QMessageBox.critical(self, "Category Error", str(error))

    def delete_selected_category(self) -> None:
        item = self.categories_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a category first.")
            return
        category_id = int(item.data(Qt.ItemDataRole.UserRole))
        answer = QMessageBox.question(
            self,
            "Delete Category",
            "Delete this category? Existing tasks will remain but become uncategorized.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            if remove_category(category_id):
                self.categoriesChanged.emit()
                QMessageBox.information(self, "Success", "Category deleted.")
            else:
                QMessageBox.warning(self, "Not Found", "Category was not found.")
        except Exception as error:
            QMessageBox.critical(self, "Category Error", str(error))
