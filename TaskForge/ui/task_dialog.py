
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QComboBox,
    QDateEdit,
    QCheckBox,
    QDialogButtonBox,
    QMessageBox,
    QWidget,
    QHBoxLayout
)
from PyQt6.QtCore import QDate

from database.category_repository import get_all_categories


class TaskDialog(QDialog):

    def __init__(self, parent=None, task=None):
        super().__init__(parent)

        self.setWindowTitle("Create New Task")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        form = QFormLayout()

        # Task title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title")
        form.addRow("Title:", self.title_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Describe your task..."
        )
        self.description_input.setFixedHeight(85)
        form.addRow("Description:", self.description_input)

        # Importance
        self.importance_input = QSpinBox()
        self.importance_input.setRange(1, 10)
        self.importance_input.setValue(5)
        form.addRow("Importance (1-10):", self.importance_input)

        # Urgency
        self.urgency_input = QSpinBox()
        self.urgency_input.setRange(1, 10)
        self.urgency_input.setValue(5)
        form.addRow("Urgency (1-10):", self.urgency_input)

        # Difficulty
        self.difficulty_input = QSpinBox()
        self.difficulty_input.setRange(1, 10)
        self.difficulty_input.setValue(5)
        form.addRow("Difficulty (1-10):", self.difficulty_input)

        # Deadline
        deadline_layout = QHBoxLayout()

        self.deadline_checkbox = QCheckBox("Set deadline")

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("yyyy-MM-dd")
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setEnabled(False)

        self.deadline_checkbox.toggled.connect(
            self.deadline_input.setEnabled
        )

        deadline_layout.addWidget(self.deadline_checkbox)
        deadline_layout.addWidget(self.deadline_input)

        deadline_widget = QWidget()
        deadline_widget.setLayout(deadline_layout)

        form.addRow("Deadline:", deadline_widget)

        # Status
        self.status_input = QComboBox()

        self.status_input.addItem("New", "new")
        self.status_input.addItem("In Progress", "in_progress")
        self.status_input.addItem("Completed", "completed")

        form.addRow("Status:", self.status_input)

        # Category
        self.category_input = QComboBox()
        self.category_input.addItem("No category", None)

        categories = get_all_categories()

        for category in categories:
            category_id = category[0]
            category_name = category[1]

            self.category_input.addItem(
                category_name,
                category_id
            )

        form.addRow("Category:", self.category_input)
        # Load existing task data when editing
        if task is not None:
            self.title_input.setText(task[1])

            self.description_input.setPlainText(
                task[2] or ""
            )

            self.importance_input.setValue(task[3])
            self.urgency_input.setValue(task[4])
            self.difficulty_input.setValue(task[5])

            if task[6]:
                task_date = QDate.fromString(
                    task[6],
                    "yyyy-MM-dd"
                )

                if task_date.isValid():
                    self.deadline_checkbox.setChecked(True)
                    self.deadline_input.setDate(task_date)

            status_index = self.status_input.findData(task[7])

            if status_index >= 0:
                self.status_input.setCurrentIndex(status_index)

            category_index = self.category_input.findData(task[8])

            if category_index >= 0:
                self.category_input.setCurrentIndex(category_index)

        main_layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        main_layout.addWidget(buttons)

    def validate_and_accept(self):

        if not self.title_input.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Task",
                "Task title cannot be empty."
            )
            return

        self.accept()

    def get_data(self):

        deadline = None

        if self.deadline_checkbox.isChecked():
            deadline = self.deadline_input.date().toString(
                "yyyy-MM-dd"
            )

        return {
            "title": self.title_input.text().strip(),
            "description": (
                self.description_input.toPlainText().strip() or None
            ),
            "importance": self.importance_input.value(),
            "urgency": self.urgency_input.value(),
            "difficulty": self.difficulty_input.value(),
            "deadline": deadline,
            "status": self.status_input.currentData(),
            "category_id": self.category_input.currentData()
        }
