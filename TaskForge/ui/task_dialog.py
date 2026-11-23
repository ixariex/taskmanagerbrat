

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.category_repository import get_all_categories
from ui.dialog_theme import DIALOG_STYLESHEET

class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Edit Task" if task is not None else "Create New Task")
        self.setMinimumWidth(470)

        main_layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setVerticalSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title")
        form.addRow("Title:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe your task...")
        self.description_input.setFixedHeight(90)
        form.addRow("Description:", self.description_input)

        self.importance_input = self._make_score_box()
        form.addRow("Importance (1–10):", self.importance_input)

        self.urgency_input = self._make_score_box()
        form.addRow("Urgency (1–10):", self.urgency_input)

        self.difficulty_input = self._make_score_box()
        form.addRow("Difficulty (1–10):", self.difficulty_input)

        deadline_row = QHBoxLayout()
        self.deadline_checkbox = QCheckBox("Set deadline")
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("yyyy-MM-dd")
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setEnabled(False)
        self.deadline_checkbox.toggled.connect(self.deadline_input.setEnabled)
        deadline_row.addWidget(self.deadline_checkbox)
        deadline_row.addWidget(self.deadline_input)
        deadline_widget = QWidget()
        deadline_widget.setLayout(deadline_row)
        form.addRow("Deadline:", deadline_widget)

        self.status_input = QComboBox()
        self.status_input.addItem("New", "new")
        self.status_input.addItem("In Progress", "in_progress")
        self.status_input.addItem("Completed", "completed")
        form.addRow("Status:", self.status_input)

        self.category_input = QComboBox()
        self.category_input.addItem("No category", None)
        for category in get_all_categories():
            self.category_input.addItem(category[1], category[0])
        form.addRow("Category:", self.category_input)

        if task is not None:
            self._load_task(task)

        main_layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setStyleSheet(DIALOG_STYLESHEET)


    @staticmethod
    def _make_score_box() -> QSpinBox:
        box = QSpinBox()
        box.setRange(1, 10)
        box.setValue(5)
        return box

    def _load_task(self, task: tuple) -> None:
        """Populate controls from a DB row: id, title, ..., category_id."""
        self.title_input.setText(task[1] or "")
        self.description_input.setPlainText(task[2] or "")
        self.importance_input.setValue(int(task[3] or 5))
        self.urgency_input.setValue(int(task[4] or 5))
        self.difficulty_input.setValue(int(task[5] or 5))

        deadline = task[6]
        if deadline:
            parsed_date = QDate.fromString(deadline, "yyyy-MM-dd")
            if parsed_date.isValid():
                self.deadline_input.setDate(parsed_date)
                self.deadline_checkbox.setChecked(True)

        status_index = self.status_input.findData(task[7])
        if status_index >= 0:
            self.status_input.setCurrentIndex(status_index)

        category_id = task[8] if len(task) > 8 else None
        category_index = self.category_input.findData(category_id)
        self.category_input.setCurrentIndex(
            category_index if category_index >= 0 else 0
        )

    def validate_and_accept(self) -> None:
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self, "Invalid Task", "Task title cannot be empty."
            )
            self.title_input.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        deadline = None
        if self.deadline_checkbox.isChecked():
            deadline = self.deadline_input.date().toString("yyyy-MM-dd")

        return {
            "title": self.title_input.text().strip(),
            "description": self.description_input.toPlainText().strip() or None,
            "importance": self.importance_input.value(),
            "urgency": self.urgency_input.value(),
            "difficulty": self.difficulty_input.value(),
            "deadline": deadline,
            "status": self.status_input.currentData(),
            "category_id": self.category_input.currentData(),
        }
