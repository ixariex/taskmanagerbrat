from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.task_manager import edit_task, get_task, remove_task, set_task_category
from optimizer_bridge import (
    calculate_task_priority,
    optimize_tasks as optimize_task_rows,
)
from ui.silent_message_box import SilentMessageBox as QMessageBox
from ui.styles import PAGE_COMMON_STYLESHEET
from ui.task_dialog import TaskDialog


class TasksWidget(QWidget):
    tasksChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("tasksPage")
        self.setStyleSheet(PAGE_COMMON_STYLESHEET)

        self.all_tasks: list = []
        self.all_categories: list = []
        self.optimized_task_order: dict[int, int] = {}
        self.optimized_task_priorities: dict[int, float] = {}
        self.optimized_task_source = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(13)

        header = QVBoxLayout()
        header.setSpacing(4)
        eyebrow = QLabel("TASKFORGE / WORKSPACE")
        eyebrow.setObjectName("pageEyebrow")
        title = QLabel("My Tasks")
        title.setObjectName("heroTitle")
        subtitle = QLabel("Manage your tasks and stay productive.")
        subtitle.setObjectName("heroSubtitle")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Filter Panel
        filter_panel = QFrame()
        filter_panel.setObjectName("contentPanel")
        filter_layout = QVBoxLayout(filter_panel)
        filter_layout.setContentsMargins(14, 13, 14, 13)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks by title or description...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.refresh_task_list)
        filter_layout.addWidget(self.search_input)

        filters = QHBoxLayout()
        filters.setSpacing(9)

        self.status_filter = QComboBox()
        self.status_filter.addItem("All statuses", "all")
        self.status_filter.addItem("New", "new")
        self.status_filter.addItem("In Progress", "in_progress")
        self.status_filter.addItem("Completed", "completed")
        self.status_filter.currentIndexChanged.connect(self.refresh_task_list)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All categories", "all")
        self.category_filter.addItem("No category", "uncategorized")
        self.category_filter.currentIndexChanged.connect(self.refresh_task_list)

        self.sort_filter = QComboBox()
        self.sort_filter.addItem("Newest first", "newest")
        self.sort_filter.addItem("Title A–Z", "title")
        self.sort_filter.addItem("Deadline soonest", "deadline")
        self.sort_filter.addItem("Importance highest", "importance")
        self.sort_filter.addItem("Urgency highest", "urgency")
        self.sort_filter.addItem("C++ Priority", "priority")
        self.sort_filter.currentIndexChanged.connect(self.refresh_task_list)

        filters.addWidget(self.status_filter, 1)
        filters.addWidget(self.category_filter, 1)
        filters.addWidget(self.sort_filter, 1)
        filter_layout.addLayout(filters)
        layout.addWidget(filter_panel)

        # Task List Panel
        task_panel = QFrame()
        task_panel.setObjectName("contentPanel")
        task_layout = QVBoxLayout(task_panel)
        task_layout.setContentsMargins(14, 13, 14, 14)
        task_layout.setSpacing(11)

        list_header = QHBoxLayout()
        section_title = QLabel("Your Tasks")
        section_title.setObjectName("sectionTitle")
        self.task_count_label = QLabel("0 tasks")
        self.task_count_label.setObjectName("countBadge")
        list_header.addWidget(section_title)
        list_header.addStretch()
        list_header.addWidget(self.task_count_label)
        task_layout.addLayout(list_header)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("secondaryButton")
        edit_button.clicked.connect(lambda: self.edit_selected_task())

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self.delete_selected_task)

        optimize_button = QPushButton("Optimize Tasks")
        optimize_button.setObjectName("primaryButton")
        optimize_button.clicked.connect(self.optimize_task_list)

        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()
        actions.addWidget(optimize_button)
        task_layout.addLayout(actions)

        self.tasks_list = QListWidget()
        self.tasks_list.setObjectName("cardList")
        self.tasks_list.setSpacing(4)
        self.tasks_list.setWordWrap(True)
        self.tasks_list.itemDoubleClicked.connect(self.edit_selected_task)
        task_layout.addWidget(self.tasks_list, 1)

        layout.addWidget(task_panel, 1)

    @staticmethod
    def _is_overdue(task) -> bool:
        return bool(task[6] and task[7] != "completed" and task[6] < date.today().isoformat())

    @staticmethod
    def _format_task(task, display_number: int) -> str:
        deadline = task[6] or "No deadline"
        status = task[7].replace("_", " ").title()
        return f"#{display_number}   {task[1]}   |   {status}   |   Deadline: {deadline}"

    @staticmethod
    def _optimizer_signature(tasks: list) -> tuple:
        return tuple(
            (int(t[0]), int(t[3]), int(t[4]), int(t[5]), str(t[7]))
            for t in tasks
            if t[7] in {"new", "in_progress"}
        )

    def refresh_data(self, tasks: list, categories: list) -> None:
        self.all_tasks = tasks
        self.all_categories = categories

        current_source = self._optimizer_signature(self.all_tasks)
        if self.optimized_task_source is not None and current_source != self.optimized_task_source:
            self.optimized_task_order = {}
            self.optimized_task_priorities = {}
            self.optimized_task_source = None

            if self.sort_filter.currentData() == "priority":
                self.sort_filter.blockSignals(True)
                self.sort_filter.setCurrentIndex(self.sort_filter.findData("newest"))
                self.sort_filter.blockSignals(False)

        self._refresh_category_filter()
        self.refresh_task_list()

    def _refresh_category_filter(self) -> None:
        current_value = self.category_filter.currentData()
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All categories", "all")
        self.category_filter.addItem("No category", "uncategorized")
        for category in self.all_categories:
            self.category_filter.addItem(category[1], category[0])
        index = self.category_filter.findData(current_value)
        self.category_filter.setCurrentIndex(index if index >= 0 else 0)
        self.category_filter.blockSignals(False)

    def optimize_task_list(self) -> None:
        try:
            active_tasks = [t for t in self.all_tasks if t[7] in {"new", "in_progress"}]
            if not active_tasks:
                QMessageBox.information(self, "Task Optimizer", "There are no unfinished tasks to optimize.")
                return

            optimized_tasks = optimize_task_rows(active_tasks)
            if not optimized_tasks:
                QMessageBox.information(self, "Task Optimizer", "No tasks were returned by the optimizer.")
                return

            self.optimized_task_order = {int(t[0]): idx for idx, t in enumerate(optimized_tasks)}
            self.optimized_task_priorities = {
                int(t[0]): calculate_task_priority(t) for t in optimized_tasks
            }
            self.optimized_task_source = self._optimizer_signature(active_tasks)

            self.sort_filter.setCurrentIndex(self.sort_filter.findData("priority"))
            self.refresh_task_list()

            QMessageBox.information(
                self,
                "Optimization Complete",
                f"Successfully optimized {len(optimized_tasks)} tasks!",
            )
        except Exception as error:
            QMessageBox.critical(self, "Optimization Error", f"Could not optimize tasks:\n{error}")

    def refresh_task_list(self, *_args) -> None:
        tasks = list(self.all_tasks)
        query = self.search_input.text().strip().casefold()
        status_value = self.status_filter.currentData()
        category_value = self.category_filter.currentData()
        sort_value = self.sort_filter.currentData()

        if query:
            tasks = [
                t for t in tasks
                if query in (t[1] or "").casefold() or query in (t[2] or "").casefold()
            ]

        if status_value != "all":
            tasks = [t for t in tasks if t[7] == status_value]

        if category_value == "uncategorized":
            tasks = [t for t in tasks if t[8] is None]
        elif category_value != "all":
            tasks = [t for t in tasks if t[8] == category_value]

        task_count = len(tasks)
        self.task_count_label.setText(f"{task_count} task{'s' if task_count != 1 else ''}")

        if sort_value == "title":
            tasks.sort(key=lambda t: (t[1] or "").casefold())
        elif sort_value == "deadline":
            tasks.sort(key=lambda t: (t[6] is None, t[6] or "9999-12-31"))
        elif sort_value == "importance":
            tasks.sort(key=lambda t: t[3], reverse=True)
        elif sort_value == "urgency":
            tasks.sort(key=lambda t: t[4], reverse=True)
        elif sort_value == "priority":
            tasks.sort(
                key=lambda t: (
                    t[7] == "completed",
                    self.optimized_task_order.get(t[0], float("inf")),
                )
            )
        else:
            tasks.sort(key=lambda t: t[0], reverse=True)

        self.tasks_list.clear()
        for display_number, task in enumerate(tasks, start=1):
            task_text = self._format_task(task, display_number)
            if task[0] in self.optimized_task_priorities:
                priority = self.optimized_task_priorities[task[0]]
                task_text += f"   |   Priority: {priority:.2f}"

            item = QListWidgetItem(task_text)
            item.setData(Qt.ItemDataRole.UserRole, task[0])
            if self._is_overdue(task):
                item.setForeground(QBrush(QColor("#E9AFCF")))
            self.tasks_list.addItem(item)

    def edit_selected_task(self, item: QListWidgetItem | None = None) -> None:
        if not isinstance(item, QListWidgetItem):
            item = self.tasks_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a task first.")
            return
        task_id = item.data(Qt.ItemDataRole.UserRole)
        if task_id is None:
            QMessageBox.warning(self, "Invalid Selection", "Task ID is missing.")
            return

        try:
            task = get_task(int(task_id))
            if task is None:
                QMessageBox.warning(self, "Not Found", "Task does not exist.")
                self.tasksChanged.emit()
                return
            dialog = TaskDialog(self, task=task)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            if not edit_task(
                int(task_id),
                data["title"],
                data["description"],
                data["importance"],
                data["urgency"],
                data["difficulty"],
                data["deadline"],
                data["status"],
            ):
                raise RuntimeError("Task could not be updated")
            if not set_task_category(int(task_id), data["category_id"]):
                raise RuntimeError("Task category could not be updated")
            self.tasksChanged.emit()
            QMessageBox.information(self, "Success", "Task updated successfully!")
        except Exception as error:
            QMessageBox.critical(self, "Edit Error", f"Could not edit task:\n{error}")

    def delete_selected_task(self) -> None:
        item = self.tasks_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a task first.")
            return
        task_id = item.data(Qt.ItemDataRole.UserRole)
        answer = QMessageBox.question(
            self,
            "Delete Task",
            "Are you sure you want to delete this task?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            if remove_task(int(task_id)):
                self.tasksChanged.emit()
                QMessageBox.information(self, "Success", "Task deleted successfully!")
            else:
                QMessageBox.warning(self, "Not Found", "Task was not found.")
        except Exception as error:
            QMessageBox.critical(self, "Delete Error", str(error))
