

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from ui.dialog_theme import DIALOG_STYLESHEET

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self._color = category[2] if category else "#A58AF5"
        self.setWindowTitle("Edit Category" if category else "Create Category")
        self.setMinimumWidth(390)

        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setVerticalSpacing(14)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Study, Work, Personal")
        form.addRow("Category name:", self.name_input)

        color_row = QHBoxLayout()
        self.color_preview = QLabel("      ")
        self.color_preview.setFixedSize(42, 28)
        self.color_button = QPushButton("Choose color")
        self.color_button.clicked.connect(self.choose_color)
        color_row.addWidget(self.color_preview)
        color_row.addWidget(self.color_button)
        color_row.addStretch()

        color_widget = QWidget()
        color_widget.setLayout(color_row)
        form.addRow("Color:", color_widget)
        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        if category:
            self.name_input.setText(category[1])
        self.setStyleSheet(DIALOG_STYLESHEET)

    def choose_color(self):
        dialog = QColorDialog(
            QColor(self._color),
            self
        )

        dialog.setWindowTitle("Choose Category Color")

        dialog.setOption(
            QColorDialog.ColorDialogOption.DontUseNativeDialog,
            True
        )

        dialog.setStyleSheet(DIALOG_STYLESHEET)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.selectedColor()

            if selected.isValid():
                self._color = selected.name()
                self.update_color_preview()

    def update_color_preview(self):
        self.color_preview.setStyleSheet(
            f"""
            background-color: {self._color};
            border: 1px solid #57466B;
            border-radius: 7px;
            """
        )

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Invalid category", "Enter a category name.")
            self.name_input.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {"name": self.name_input.text().strip(), "color": self._color}
