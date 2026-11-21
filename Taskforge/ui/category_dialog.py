

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


class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self._color = category[2] if category else "#3498db"
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
        self.update_color_preview()

    def choose_color(self):
        selected = QColorDialog.getColor(QColor(self._color), self, "Choose category color")
        if selected.isValid():
            self._color = selected.name()
            self.update_color_preview()

    def update_color_preview(self):
        self.color_preview.setStyleSheet(
            f"background-color: {self._color}; border: 1px solid #9aa3b2; border-radius: 5px;"
        )

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Invalid category", "Enter a category name.")
            self.name_input.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {"name": self.name_input.text().strip(), "color": self._color}
