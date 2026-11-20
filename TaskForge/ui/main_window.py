"""Main PyQt6 window for TaskForge."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)

from core.task_manager import (
    create_task,
    edit_task,
    get_task,
    get_tasks,
    remove_task,
    set_task_category,
)
from database.category_repository import get_all_categories
from ui.task_dialog import TaskDialog


STYLESHEET = """
QWidget#appRoot { background-color: #f4f6fa; color: #20283a; font-family: "Segoe UI"; font-size: 14px; }
QWidget#sidebar { background-color: #172033; }
QLabel#brand { color: white; font-size: 25px; font-weight: bold; }
QLabel#sidebarSubtitle { color: #94a3b8; font-size: 12px; }
QPushButton#navButton { background: transparent; color: #cbd5e1; border: none; border-radius: 8px; text-align: left; padding: 13px; font-size: 14px; }
QPushButton#navButton:hover { background-color: #283650; color: white; }
QPushButton#navButton:checked { background-color: #3658d4; color: white; font-weight: bold; }
QLabel#pageTitle { font-size: 27px; font-weight: bold; color: #172033; }
QLabel#pageSubtitle { color: #7b8497; font-size: 13px; }
QFrame#statCard { background: white; border: 1px solid #e5e9f0; border-radius: 12px; }
QLabel#statTitle { color: #7b8497; font-size: 13px; }
QLabel#statValue { color: #172033; font-size: 29px; font-weight: bold; }
QListWidget { background: white; border: 1px solid #e5e9f0; border-radius: 10px; padding: 8px; outline: none; }
QListWidget::item { padding: 12px; border-bottom: 1px solid #f0f2f6; }
QListWidget::item:selected { background-color: #e9efff; color: #294bb5; }
QPushButton#primaryButton { background-color: #3658d4; color: white; border: none; border-radius: 7px; padding: 10px 18px; }
QPushButton#primaryButton:hover { background-color: #2948b8; }
QPushButton#dangerButton { background-color: #dc4444; color: white; border: none; border-radius: 7px; padding: 10px 18px; }
QPushButton#dangerButton:hover { background-color: #bd3030; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskForge")
        self.resize(1150, 750)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(STYLESHEET)

        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.create_sidebar(root_layout)
        self.create_content(root_layout)
        self.switch_page(0)

    def create_sidebar(self, root_layout):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 25, 18, 20)
        layout.setSpacing(10)

        brand = QLabel("TaskForge")
        brand.setObjectName("brand")
        layout.addWidget(brand)

        subtitle = QLabel("PRODUCTIVITY MANAGER")
        subtitle.setObjectName("sidebarSubtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(35)

        self.nav_buttons = []
        for index, page_name in enumerate(
            ["Dashboard", "My Tasks", "Categories", "Completed"]
        ):
            button = QPushButton("   " + page_name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked=False, i=index: self.switch_page(i)
            )
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch()
        version = QLabel("TaskForge v1.0")
        version.setObjectName("sidebarSubtitle")
        layout.addWidget(version)
        root_layout.addWidget(sidebar)

    def create_content(self, root_layout):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 28, 35, 28)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        self.page_title = QLabel()
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel()
        self.page_subtitle.setObjectName("pageSubtitle")
        title_layout.addWidget(self.page_title)
        title_layout.addWidget(self.page_subtitle)
        header.addLayout(title_layout)
        header.addStretch()

        add_button = QPushButton("+ Add Task")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(
            lambda checked=False: self.open_add_task()
        )
        header.addWidget(add_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("primaryButton")
        refresh_button.clicked.connect(
            lambda checked=False: self.refresh_data()
        )
        header.addWidget(refresh_button)
        layout.addLayout(header)

        self.stack = QStackedWidget()
        self.dashboard_page = self.build_dashboard()
        self.tasks_page = self.build_tasks_page()
        self.categories_page = self.build_categories_page()
        self.completed_page = self.build_completed_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.categories_page)
        self.stack.addWidget(self.completed_page)
        layout.addWidget(self.stack)
        root_layout.addWidget(content)

    @staticmethod
    def make_stat_card(title):
        card = QFrame()
        card.setObjectName("statCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        value_label = QLabel("0")
        value_label.setObjectName("statValue")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        card1, self.total_value = self.make_stat_card("Total Tasks")
        card2, self.progress_value = self.make_stat_card("In Progress")
        card3, self.completed_value = self.make_stat_card("Completed")
        cards_layout.addWidget(card1)
        cards_layout.addWidget(card2)
        cards_layout.addWidget(card3)
        layout.addLayout(cards_layout)

        recent_title = QLabel("Recent Tasks")
        recent_title.setStyleSheet("font-size: 17px; font-weight: bold;")
        layout.addWidget(recent_title)
        self.recent_list = QListWidget()
        layout.addWidget(self.recent_list)
        return page

    def build_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        actions = QHBoxLayout()

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("primaryButton")
        # Use a zero-argument wrapper for QPushButton.clicked(bool).
        edit_button.clicked.connect(
            lambda checked=False: self.edit_selected_task()
        )

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(
            lambda checked=False: self.delete_selected_task()
        )

        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.tasks_list = QListWidget()
        # Use an explicit wrapper because itemDoubleClicked emits an item.
        self.tasks_list.itemDoubleClicked.connect(
            lambda item: self.edit_selected_task(item)
        )
        layout.addWidget(self.tasks_list)
        return page

    def build_categories_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.categories_list = QListWidget()
        layout.addWidget(self.categories_list)
        return page

    def build_completed_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.completed_list = QListWidget()
        layout.addWidget(self.completed_list)
        return page

    def switch_page(self, index):
        page_titles = [
            ("Dashboard", "Your productivity overview"),
            ("My Tasks", "Manage all your tasks"),
            ("Categories", "Organize your tasks"),
            ("Completed", "Your finished tasks"),
        ]
        if not 0 <= index < len(page_titles):
            return
        self.stack.setCurrentIndex(index)
        self.page_title.setText(page_titles[index][0])
        self.page_subtitle.setText(page_titles[index][1])
        for button_index, button in enumerate(self.nav_buttons):
            button.setChecked(button_index == index)
        self.refresh_data()

    @staticmethod
    def format_task(task):
        task_id, title = task[0], task[1]
        deadline = task[6] or "No deadline"
        status = task[7].replace("_", " ").title()
        return f"#{task_id}   {title}   |   {status}   |   Deadline: {deadline}"

    def refresh_data(self):
        try:
            tasks = sorted(get_tasks(), key=lambda row: row[0], reverse=True)
            categories = get_all_categories()
            completed = [task for task in tasks if task[7] == "completed"]
            in_progress = [task for task in tasks if task[7] == "in_progress"]

            self.total_value.setText(str(len(tasks)))
            self.progress_value.setText(str(len(in_progress)))
            self.completed_value.setText(str(len(completed)))

            self.recent_list.clear()
            for task in tasks[:5]:
                self.recent_list.addItem(self.format_task(task))

            self.tasks_list.clear()
            for task in tasks:
                item = QListWidgetItem(self.format_task(task))
                item.setData(Qt.ItemDataRole.UserRole, task[0])
                self.tasks_list.addItem(item)

            self.categories_list.clear()
            for category in categories:
                self.categories_list.addItem(
                    f"#{category[0]}   {category[1]}   |   {category[2]}"
                )

            self.completed_list.clear()
            for task in completed:
                self.completed_list.addItem(self.format_task(task))

        except Exception as error:
            QMessageBox.critical(
                self, "Loading Error", f"Could not load data:\n{error}"
            )

    def open_add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            create_task(**dialog.get_data())
            self.refresh_data()
            QMessageBox.information(self, "Success", "Task created successfully!")
        except Exception as error:
            QMessageBox.critical(
                self, "Error", f"Could not create task:\n{error}"
            )

    def edit_selected_task(self, item=None):
        """Edit the selected task. Also accepts an item from double-click."""
        if not isinstance(item, QListWidgetItem):
            item = self.tasks_list.currentItem()

        if item is None:
            QMessageBox.warning(
                self, "No Selection", "Please select a task first."
            )
            return

        task_id = item.data(Qt.ItemDataRole.UserRole)
        if task_id is None:
            QMessageBox.warning(self, "Invalid Selection", "Task ID is missing.")
            return

        try:
            task = get_task(int(task_id))
            if task is None:
                QMessageBox.warning(self, "Not Found", "Task does not exist.")
                self.refresh_data()
                return

            # The dialog is created only after the selected DB row is loaded.
            dialog = TaskDialog(self, task=task)
            result = dialog.exec()
            if result != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()
            updated = edit_task(
                task_id=int(task_id),
                title=data["title"],
                description=data["description"],
                importance=data["importance"],
                urgency=data["urgency"],
                difficulty=data["difficulty"],
                deadline=data["deadline"],
                status=data["status"],
            )
            if not updated:
                raise RuntimeError("Task could not be updated.")

            category_updated = set_task_category(
                int(task_id), data["category_id"]
            )
            if not category_updated:
                raise RuntimeError("Category assignment could not be updated.")

            self.refresh_data()
            QMessageBox.information(self, "Success", "Task updated successfully!")

        except Exception as error:
            QMessageBox.critical(
                self, "Edit Error", f"Could not edit task:\n{error}"
            )

    def delete_selected_task(self):
        item = self.tasks_list.currentItem()
        if item is None:
            QMessageBox.warning(
                self, "No Selection", "Please select a task first."
            )
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
                self.refresh_data()
                QMessageBox.information(self, "Success", "Task deleted successfully!")
            else:
                QMessageBox.warning(self, "Not Found", "Task was not found.")
        except Exception as error:
            QMessageBox.critical(
                self, "Delete Error", f"Could not delete task:\n{error}"
            )
