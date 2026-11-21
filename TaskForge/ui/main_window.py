

from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)

from core.category_manager import (
    create_category,
    edit_category,
    get_categories,
    get_category,
    remove_category,
)
from core.task_manager import (
    create_task,
    edit_task,
    get_task,
    get_tasks,
    remove_task,
    set_task_category,
)
from ui.category_dialog import CategoryDialog
from ui.task_dialog import TaskDialog


STYLESHEET = """
QWidget#appRoot { background: #f4f6fa; color: #20283a; font-family: "Segoe UI"; font-size: 14px; }
QWidget#sidebar { background: #172033; }
QLabel#brand { color: white; font-size: 25px; font-weight: bold; }
QLabel#sidebarSubtitle { color: #94a3b8; font-size: 12px; }
QPushButton#navButton { background: transparent; color: #cbd5e1; border: none; border-radius: 8px; text-align: left; padding: 13px; font-size: 14px; }
QPushButton#navButton:hover { background: #283650; color: white; }
QPushButton#navButton:checked { background: #3658d4; color: white; font-weight: bold; }
QLabel#pageTitle { font-size: 27px; font-weight: bold; color: #172033; }
QLabel#pageSubtitle { color: #7b8497; font-size: 13px; }
QFrame#statCard { background: white; border: 1px solid #e5e9f0; border-radius: 12px; }
QLabel#statTitle { color: #7b8497; font-size: 13px; }
QLabel#statValue { color: #172033; font-size: 29px; font-weight: bold; }
QListWidget { background: white; border: 1px solid #e5e9f0; border-radius: 10px; padding: 8px; outline: none; }
QListWidget::item { padding: 12px; border-bottom: 1px solid #f0f2f6; }
QListWidget::item:selected { background: #e9efff; color: #294bb5; }
QLineEdit, QComboBox { background: white; border: 1px solid #dce2ec; border-radius: 7px; padding: 9px; }
QPushButton#primaryButton { background: #3658d4; color: white; border: none; border-radius: 7px; padding: 10px 18px; }
QPushButton#primaryButton:hover { background: #2948b8; }
QPushButton#dangerButton { background: #dc4444; color: white; border: none; border-radius: 7px; padding: 10px 18px; }
QPushButton#dangerButton:hover { background: #bd3030; }
QPushButton#secondaryButton { background: #e7ebf4; color: #25324a; border: none; border-radius: 7px; padding: 10px 18px; }
QPushButton#secondaryButton:hover { background: #d9e0ed; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskForge")
        self.resize(1180, 780)
        self.setMinimumSize(950, 620)
        self.setStyleSheet(STYLESHEET)
        self.all_tasks = []
        self.all_categories = []

        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.create_sidebar(root_layout)
        self.create_content(root_layout)
        self.switch_page(0)

    # ---------- Layout ----------
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
        for index, page_name in enumerate(["Dashboard", "My Tasks", "Categories", "Completed"]):
            button = QPushButton("   " + page_name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.switch_page(i))
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch()
        version = QLabel("TaskForge v1.1")
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

        self.add_task_button = QPushButton("+ Add Task")
        self.add_task_button.setObjectName("primaryButton")
        self.add_task_button.clicked.connect(lambda checked=False: self.open_add_task())
        header.addWidget(self.add_task_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.clicked.connect(lambda checked=False: self.refresh_data())
        header.addWidget(refresh_button)
        layout.addLayout(header)

        self.stack = QStackedWidget()
        self.dashboard_page = self.build_dashboard()
        self.tasks_page = self.build_tasks_page()
        self.categories_page = self.build_categories_page()
        self.completed_page = self.build_completed_page()
        for page in (self.dashboard_page, self.tasks_page, self.categories_page, self.completed_page):
            self.stack.addWidget(page)
        layout.addWidget(self.stack)
        root_layout.addWidget(content)

    @staticmethod
    def make_stat_card(title):
        card = QFrame()
        card.setObjectName("statCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        value_label = QLabel("0")
        value_label.setObjectName("statValue")
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        return card, value_label

    # ---------- Pages ----------
    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        cards = QHBoxLayout()
        cards.setSpacing(15)
        card, self.total_value = self.make_stat_card("Total Tasks")
        cards.addWidget(card)
        card, self.progress_value = self.make_stat_card("In Progress")
        cards.addWidget(card)
        card, self.completed_value = self.make_stat_card("Completed")
        cards.addWidget(card)
        card, self.overdue_value = self.make_stat_card("Overdue")
        cards.addWidget(card)
        layout.addLayout(cards)

        recent_title = QLabel("Recent Tasks")
        recent_title.setStyleSheet("font-size: 17px; font-weight: bold;")
        layout.addWidget(recent_title)
        self.recent_list = QListWidget()
        layout.addWidget(self.recent_list)
        return page

    def build_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        filters = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks by title or description...")
        self.search_input.textChanged.connect(self.refresh_task_list)
        filters.addWidget(self.search_input, 2)

        self.status_filter = QComboBox()
        self.status_filter.addItem("All statuses", "all")
        self.status_filter.addItem("New", "new")
        self.status_filter.addItem("In Progress", "in_progress")
        self.status_filter.addItem("Completed", "completed")
        self.status_filter.currentIndexChanged.connect(self.refresh_task_list)
        filters.addWidget(self.status_filter)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All categories", "all")
        self.category_filter.addItem("No category", "uncategorized")
        self.category_filter.currentIndexChanged.connect(self.refresh_task_list)
        filters.addWidget(self.category_filter)

        self.sort_filter = QComboBox()
        self.sort_filter.addItem("Newest first", "newest")
        self.sort_filter.addItem("Title A–Z", "title")
        self.sort_filter.addItem("Deadline soonest", "deadline")
        self.sort_filter.addItem("Importance highest", "importance")
        self.sort_filter.addItem("Urgency highest", "urgency")
        self.sort_filter.currentIndexChanged.connect(self.refresh_task_list)
        filters.addWidget(self.sort_filter)
        layout.addLayout(filters)

        actions = QHBoxLayout()
        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("primaryButton")
        edit_button.clicked.connect(lambda checked=False: self.edit_selected_task())
        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(lambda checked=False: self.delete_selected_task())
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(lambda item: self.edit_selected_task(item))
        layout.addWidget(self.tasks_list)
        return page

    def build_categories_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        actions = QHBoxLayout()

        add_button = QPushButton("+ Add Category")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(lambda checked=False: self.open_add_category())
        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("secondaryButton")
        edit_button.clicked.connect(lambda checked=False: self.edit_selected_category())
        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(lambda checked=False: self.delete_selected_category())
        actions.addWidget(add_button)
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.categories_list = QListWidget()
        self.categories_list.itemDoubleClicked.connect(lambda item: self.edit_selected_category(item))
        layout.addWidget(self.categories_list)
        return page

    def build_completed_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.completed_list = QListWidget()
        layout.addWidget(self.completed_list)
        return page

    def switch_page(self, index):
        pages = [
            ("Dashboard", "Your productivity overview"),
            ("My Tasks", "Search, filter and manage your tasks"),
            ("Categories", "Organize tasks with color-coded categories"),
            ("Completed", "Your finished tasks"),
        ]
        if not 0 <= index < len(pages):
            return
        self.stack.setCurrentIndex(index)
        self.page_title.setText(pages[index][0])
        self.page_subtitle.setText(pages[index][1])
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
        self.add_task_button.setVisible(index in (0, 1))
        self.refresh_data()

    @staticmethod
    def format_task(task):
        deadline = task[6] or "No deadline"
        status = task[7].replace("_", " ").title()
        title = task[1]
        return f"#{task[0]}   {title}   |   {status}   |   Deadline: {deadline}"

    @staticmethod
    def task_is_overdue(task) -> bool:
        return bool(task[6] and task[7] != "completed" and task[6] < date.today().isoformat())

    def refresh_data(self):
        try:
            self.all_tasks = get_tasks()
            self.all_categories = get_categories()

            completed = [task for task in self.all_tasks if task[7] == "completed"]
            in_progress = [task for task in self.all_tasks if task[7] == "in_progress"]
            overdue = [task for task in self.all_tasks if self.task_is_overdue(task)]

            self.total_value.setText(str(len(self.all_tasks)))
            self.progress_value.setText(str(len(in_progress)))
            self.completed_value.setText(str(len(completed)))
            self.overdue_value.setText(str(len(overdue)))

            self.recent_list.clear()
            for task in sorted(self.all_tasks, key=lambda row: row[0], reverse=True)[:5]:
                self.recent_list.addItem(self.format_task(task))

            self.refresh_category_filter()
            self.refresh_task_list()

            self.categories_list.clear()
            for category in self.all_categories:
                item = QListWidgetItem(f"{category[1]}   ({category[2]})")
                item.setData(Qt.ItemDataRole.UserRole, category[0])
                item.setForeground(QBrush(QColor(category[2])))
                self.categories_list.addItem(item)

            self.completed_list.clear()
            for task in sorted(completed, key=lambda row: row[0], reverse=True):
                item = QListWidgetItem(self.format_task(task))
                item.setData(Qt.ItemDataRole.UserRole, task[0])
                self.completed_list.addItem(item)

        except Exception as error:
            QMessageBox.critical(self, "Loading Error", f"Could not load data:\n{error}")

    def refresh_category_filter(self):
        if not hasattr(self, "category_filter"):
            return
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

    def refresh_task_list(self, *_args):
        if not hasattr(self, "tasks_list"):
            return
        tasks = list(self.all_tasks)
        query = self.search_input.text().strip().casefold()
        status_value = self.status_filter.currentData()
        category_value = self.category_filter.currentData()
        sort_value = self.sort_filter.currentData()

        if query:
            tasks = [task for task in tasks if query in (task[1] or "").casefold() or query in (task[2] or "").casefold()]
        if status_value != "all":
            tasks = [task for task in tasks if task[7] == status_value]
        if category_value == "uncategorized":
            tasks = [task for task in tasks if task[8] is None]
        elif category_value != "all":
            tasks = [task for task in tasks if task[8] == category_value]

        if sort_value == "title":
            tasks.sort(key=lambda task: (task[1] or "").casefold())
        elif sort_value == "deadline":
            tasks.sort(key=lambda task: (task[6] is None, task[6] or "9999-12-31"))
        elif sort_value == "importance":
            tasks.sort(key=lambda task: task[3], reverse=True)
        elif sort_value == "urgency":
            tasks.sort(key=lambda task: task[4], reverse=True)
        else:
            tasks.sort(key=lambda task: task[0], reverse=True)

        self.tasks_list.clear()
        for task in tasks:
            item = QListWidgetItem(self.format_task(task))
            item.setData(Qt.ItemDataRole.UserRole, task[0])
            if self.task_is_overdue(task):
                item.setForeground(QBrush(QColor("#c0392b")))
            self.tasks_list.addItem(item)

    def open_add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            create_task(**dialog.get_data())
            self.refresh_data()
            QMessageBox.information(self, "Success", "Task created successfully!")
        except Exception as error:
            QMessageBox.critical(self, "Create Error", str(error))

    def edit_selected_task(self, item=None):
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
                self.refresh_data()
                return
            dialog = TaskDialog(self, task=task)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            data = dialog.get_data()
            if not edit_task(
                int(task_id), data["title"], data["description"],
                data["importance"], data["urgency"], data["difficulty"],
                data["deadline"], data["status"],
            ):
                raise RuntimeError("Task could not be updated")
            if not set_task_category(int(task_id), data["category_id"]):
                raise RuntimeError("Task category could not be updated")
            self.refresh_data()
            QMessageBox.information(self, "Success", "Task updated successfully!")
        except Exception as error:
            QMessageBox.critical(self, "Edit Error", f"Could not edit task:\n{error}")

    def delete_selected_task(self):
        item = self.tasks_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a task first.")
            return
        task_id = item.data(Qt.ItemDataRole.UserRole)
        answer = QMessageBox.question(
            self, "Delete Task", "Are you sure you want to delete this task?",
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
            QMessageBox.critical(self, "Delete Error", str(error))

    def open_add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_data()
        try:
            if not create_category(**data):
                QMessageBox.warning(self, "Duplicate Category", "A category with this name already exists.")
                return
            self.refresh_data()
        except Exception as error:
            QMessageBox.critical(self, "Category Error", str(error))

    def edit_selected_category(self, item=None):
        if not isinstance(item, QListWidgetItem):
            item = self.categories_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a category first.")
            return
        category_id = item.data(Qt.ItemDataRole.UserRole)
        category = get_category(int(category_id))
        if category is None:
            QMessageBox.warning(self, "Not Found", "Category does not exist.")
            self.refresh_data()
            return
        dialog = CategoryDialog(self, category=category)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            if not edit_category(int(category_id), **dialog.get_data()):
                QMessageBox.warning(self, "Update Failed", "Name may already be in use.")
                return
            self.refresh_data()
        except Exception as error:
            QMessageBox.critical(self, "Category Error", str(error))

    def delete_selected_category(self):
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
                self.refresh_data()
                QMessageBox.information(self, "Success", "Category deleted.")
            else:
                QMessageBox.warning(self, "Not Found", "Category was not found.")
        except Exception as error:
            QMessageBox.critical(self, "Category Error", str(error))
