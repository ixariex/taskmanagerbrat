

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
    QProgressBar,
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
from optimizer_bridge import (
    optimize_tasks as optimize_task_rows,
    calculate_task_priority,
)
from ui.category_dialog import CategoryDialog
from ui.task_dialog import TaskDialog

from ui.pomodoro_widget import PomodoroWidget
from ui.history_widget import HistoryWidget
from ui.statistics_widget import StatisticsWidget



STYLESHEET = """

QWidget#appRoot {
    background-color: #100D16;
    color: #F2EAF9;
    font-family: "Segoe UI";
    font-size: 14px;
}

QWidget#sidebar {
    background-color: #0B0910;
    border-right: 1px solid #292234;
}

QLabel#brand {
    color: #D6C8F4;
    font-size: 27px;
    font-weight: bold;
}

QLabel#sidebarSubtitle {
    color: #93879F;
    font-size: 11px;
    letter-spacing: 1px;
}

QPushButton {
    background-color: #211A2D;
    color: #EDE5F8;
    border: 1px solid #382E46;
    border-radius: 8px;
    padding: 9px 14px;
}

QPushButton:hover {
    background-color: #30243E;
    border-color: #9577DB;
}

QPushButton:pressed {
    background-color: #413154;
}

QPushButton#navButton {
    background-color: transparent;
    color: #B9ADCA;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding: 13px;
    font-size: 14px;
}

QPushButton#navButton:hover {
    background-color: #211A2D;
    color: #F2EAF9;
}

QPushButton#navButton:checked {
    background-color: #342644;
    color: #D6C2FF;
    font-weight: bold;
    border-left: 3px solid #A58AF5;
}

QLabel#pageTitle {
    font-size: 28px;
    font-weight: bold;
    color: #F2EAF9;
}

QLabel#pageSubtitle {
    color: #A69AAF;
    font-size: 13px;
}

QFrame#statCard {
    background-color: #1B1624;
    border: 1px solid #33283F;
    border-radius: 14px;
}

QLabel#statTitle {
    color: #B8A9C9;
    font-size: 13px;
}

QLabel#statValue {
    color: #D6C8F4;
    font-size: 30px;
    font-weight: bold;
}

QListWidget {
    background-color: #191421;
    color: #F0E9F7;
    border: 1px solid #352A42;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    background-color: transparent;
    padding: 13px;
    border-bottom: 1px solid #30273A;
    border-radius: 6px;
}

QListWidget::item:hover {
    background-color: #282034;
}

QListWidget::item:selected {
    background-color: #392B4D;
    color: #E5D6FF;
}

QLineEdit,
QComboBox,
QTextEdit,
QDateEdit,
QSpinBox,
QTimeEdit {
    background-color: #1C1725;
    color: #F2EAF9;
    border: 1px solid #3A3048;
    border-radius: 8px;
    padding: 9px;
    selection-background-color: #8062C8;
}

QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus,
QDateEdit:focus,
QSpinBox:focus {
    border: 1px solid #A58AF5;
}

QComboBox::drop-down {
    border: none;
    width: 25px;
}

QComboBox QAbstractItemView {
    background-color: #211A2D;
    color: #F2EAF9;
    selection-background-color: #48345F;
    border: 1px solid #453654;
}

QPushButton#primaryButton {
    background-color: #8D6BD0;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #A58AF5;
    color: #150F20;
}

QPushButton#secondaryButton {
    background-color: #292236;
    color: #D6C8F4;
    border: 1px solid #443653;
    border-radius: 8px;
    padding: 10px 18px;
}

QPushButton#secondaryButton:hover {
    background-color: #392E4B;
}

QPushButton#dangerButton {
    background-color: #38202F;
    color: #F2C5DF;
    border: 1px solid #684052;
    border-radius: 8px;
    padding: 10px 18px;
}

QPushButton#dangerButton:hover {
    background-color: #553047;
    border-color: #E9AFCF;
}

QScrollBar:vertical {
    background-color: #15111C;
    width: 9px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #58446D;
    border-radius: 4px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A58AF5;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QToolTip {
    background-color: #292136;
    color: #F2EAF9;
    border: 1px solid #8D6BD0;
    padding: 5px;
}
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
        self.optimized_task_order = {}
        self.optimized_task_priorities = {}
        self.optimized_task_source = None

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

        pages = [
            "Dashboard",
            "My Tasks",
            "Categories",
            "Completed",
            "Timer",
            "History",
            "Statistics"
        ]

        for index, page_name in enumerate(pages):
            button = QPushButton("   " + page_name)
            button.setObjectName("navButton")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, i=index: self.switch_page(i)
            )

            layout.addWidget(button)
            self.nav_buttons.append(button)

        # Temporary debugging


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
        self.pomodoro_page = PomodoroWidget()
        self.history_page = HistoryWidget()
        self.statistics_page = StatisticsWidget()
        for page in (
                self.dashboard_page,
                self.tasks_page,
                self.categories_page,
                self.completed_page,
                self.pomodoro_page,
                self.history_page,
                self.statistics_page
        ):
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
        page.setObjectName("dashboardPage")

        page.setStyleSheet("""
            QWidget#dashboardPage {
                background-color: #100D16;
                color: #F2EAF9;
            }

            QWidget#dashboardPage QLabel {
                color: #F2EAF9;
                background: transparent;
            }

            QWidget#dashboardPage QLabel#statTitle {
                color: #B8A9C9;
                font-size: 13px;
            }

            QWidget#dashboardPage QLabel#statValue {
                color: #D6C8F4;
                font-size: 27px;
                font-weight: bold;
            }

            QWidget#dashboardPage QLabel#sectionTitle {
                color: #E9C5DF;
                font-size: 18px;
                font-weight: bold;
            }

            QWidget#dashboardPage QListWidget {
                background-color: #191421;
                color: #F2EAF9;
                border: 1px solid #352A42;
                border-radius: 12px;
            }

            QWidget#dashboardPage QListWidget::item {
                color: #F2EAF9;
            }

            QWidget#dashboardPage QListWidget::item:selected {
                background-color: #392B4D;
                color: #E5D6FF;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # =====================================
        # HEADER
        # =====================================

        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        eyebrow = QLabel("TASKFORGE / YOUR WORKSPACE")
        eyebrow.setStyleSheet("""
            color: #A58AF5;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
        """)

        welcome_title = QLabel("Welcome back.")
        welcome_title.setStyleSheet("""
            color: #F2EAF9;
            font-size: 27px;
            font-weight: bold;
            background: transparent;
        """)

        welcome_subtitle = QLabel(
            "Here's your productivity overview."
        )
        welcome_subtitle.setStyleSheet("""
            color: #A69AAF;
            font-size: 13px;
            background: transparent;
        """)

        header_layout.addWidget(eyebrow)
        header_layout.addWidget(welcome_title)
        header_layout.addWidget(welcome_subtitle)

        layout.addLayout(header_layout)

        # =====================================
        # STATISTICS CARDS
        # =====================================

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(13)

        card, self.total_value = self.make_stat_card(
            "Total Tasks"
        )
        cards_layout.addWidget(card)

        card, self.progress_value = self.make_stat_card(
            "In Progress"
        )
        cards_layout.addWidget(card)

        card, self.completed_value = self.make_stat_card(
            "Completed"
        )
        cards_layout.addWidget(card)

        card, self.overdue_value = self.make_stat_card(
            "Overdue"
        )
        cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # =====================================
        # BOTTOM SECTION
        # =====================================

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        # Productivity overview card
        overview_card = QFrame()
        overview_card.setObjectName("statCard")
        overview_card.setMinimumWidth(190)

        overview_layout = QVBoxLayout(overview_card)
        overview_layout.setContentsMargins(20, 18, 20, 18)
        overview_layout.setSpacing(13)

        overview_title = QLabel("Productivity Overview")
        overview_title.setObjectName("sectionTitle")

        overview_layout.addWidget(overview_title)

        rate_header = QHBoxLayout()

        rate_label = QLabel("Completion rate")
        rate_label.setStyleSheet(
            "color: #A69AAF; background: transparent;"
        )

        self.completion_rate_value = QLabel("0%")
        self.completion_rate_value.setStyleSheet("""
            color: #D6C8F4;
            font-size: 22px;
            font-weight: bold;
            background: transparent;
        """)

        rate_header.addWidget(rate_label)
        rate_header.addStretch()
        rate_header.addWidget(self.completion_rate_value)

        overview_layout.addLayout(rate_header)

        self.completion_progress = QProgressBar()
        self.completion_progress.setRange(0, 100)
        self.completion_progress.setValue(0)
        self.completion_progress.setTextVisible(False)
        self.completion_progress.setFixedHeight(9)

        self.completion_progress.setStyleSheet("""
            QProgressBar {
                background-color: #382C48;
                border: none;
                border-radius: 4px;
            }

            QProgressBar::chunk {
                background-color: #A58AF5;
                border-radius: 4px;
            }
        """)

        overview_layout.addWidget(self.completion_progress)

        self.completion_description = QLabel(
            "Complete your first task to get started."
        )
        self.completion_description.setWordWrap(True)
        self.completion_description.setStyleSheet("""
            color: #A69AAF;
            font-size: 11px;
            background: transparent;
        """)

        overview_layout.addWidget(self.completion_description)
        overview_layout.addStretch()

        bottom_layout.addWidget(overview_card, 1)

        # =====================================
        # RECENT TASKS CARD
        # =====================================

        recent_card = QFrame()
        recent_card.setObjectName("statCard")

        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(20, 18, 20, 18)
        recent_layout.setSpacing(12)

        recent_header = QHBoxLayout()

        recent_title = QLabel("Recent Tasks")
        recent_title.setObjectName("sectionTitle")

        recent_subtitle = QLabel("Your latest activity")
        recent_subtitle.setStyleSheet("""
            color: #A69AAF;
            font-size: 11px;
            background: transparent;
        """)

        recent_header.addWidget(recent_title)
        recent_header.addStretch()
        recent_header.addWidget(recent_subtitle)

        recent_layout.addLayout(recent_header)

        self.recent_list = QListWidget()
        self.recent_list.setMinimumHeight(170)
        self.recent_list.setObjectName("recentList")

        recent_layout.addWidget(self.recent_list)

        bottom_layout.addWidget(recent_card, 2)

        layout.addLayout(bottom_layout)

        layout.addStretch()

        return page

    def build_tasks_page(self):
        page = QWidget()
        page.setObjectName("tasksPage")

        page.setStyleSheet("""
            QWidget#tasksPage {
                background: transparent;
                color: #F2EAF9;
            }

            QLabel#tasksEyebrow {
                color: #A58AF5;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QLabel#tasksTitle {
                color: #F2EAF9;
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#tasksSubtitle {
                color: #A69AAF;
                font-size: 12px;
            }

            QLabel#taskCount {
                color: #D6C8F4;
                background: #30263B;
                border: 1px solid #493957;
                border-radius: 10px;
                padding: 7px 13px;
                font-weight: bold;
            }

            QLabel#sectionTitle {
                color: #E9C5DF;
                font-size: 16px;
                font-weight: bold;
            }

            QFrame#tasksFilterPanel,
            QFrame#taskListPanel {
                background-color: #1B1624;
                border: 1px solid #352A42;
                border-radius: 13px;
            }

            QLineEdit,
            QComboBox {
                background-color: #15111C;
                color: #F2EAF9;
                border: 1px solid #40344F;
                border-radius: 8px;
                padding: 10px;
                min-height: 21px;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #A58AF5;
            }

            QLineEdit::placeholder {
                color: #867A94;
            }

            QComboBox QAbstractItemView {
                background-color: #211A2D;
                color: #F2EAF9;
                border: 1px solid #493957;
                selection-background-color: #48345F;
                selection-color: white;
            }

            QListWidget {
                background-color: #15111C;
                color: #F2EAF9;
                border: 1px solid #352A42;
                border-radius: 10px;
                padding: 8px;
                outline: none;
            }

            QListWidget::item {
                background-color: #1D1727;
                color: #F2EAF9;
                padding: 14px;
                margin: 3px 1px;
                border: 1px solid #30263B;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #292136;
                border-color: #57446D;
            }

            QListWidget::item:selected {
                background-color: #392B4D;
                border-color: #A58AF5;
                color: #FFFFFF;
            }

            QPushButton#primaryButton {
                background-color: #A58AF5;
                color: #160F20;
                border: none;
                border-radius: 8px;
                padding: 11px 17px;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #BBA8FA;
            }

            QPushButton#secondaryButton {
                background-color: #30263B;
                color: #D6C8F4;
                border: 1px solid #493957;
                border-radius: 8px;
                padding: 11px 17px;
            }

            QPushButton#secondaryButton:hover {
                background-color: #443653;
            }

            QPushButton#dangerButton {
                background-color: #38202F;
                color: #F2C5DF;
                border: 1px solid #684052;
                border-radius: 8px;
                padding: 11px 17px;
            }

            QPushButton#dangerButton:hover {
                background-color: #553047;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(13)

        # =====================================
        # PAGE HEADER
        # =====================================

        header = QVBoxLayout()
        header.setSpacing(4)

        eyebrow = QLabel("TASKFORGE / WORKSPACE")
        eyebrow.setObjectName("tasksEyebrow")

        title = QLabel("My Tasks")
        title.setObjectName("tasksTitle")

        subtitle = QLabel(
            "Manage your tasks and stay productive."
        )
        subtitle.setObjectName("tasksSubtitle")

        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)

        layout.addLayout(header)

        # =====================================
        # FILTER PANEL
        # =====================================

        filter_panel = QFrame()
        filter_panel.setObjectName("tasksFilterPanel")

        filter_layout = QVBoxLayout(filter_panel)
        filter_layout.setContentsMargins(14, 13, 14, 13)
        filter_layout.setSpacing(10)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search tasks by title or description..."
        )
        self.search_input.setClearButtonEnabled(True)

        self.search_input.textChanged.connect(
            self.refresh_task_list
        )

        filter_layout.addWidget(self.search_input)

        # Filter controls
        filters = QHBoxLayout()
        filters.setSpacing(9)

        self.status_filter = QComboBox()
        self.status_filter.addItem("All statuses", "all")
        self.status_filter.addItem("New", "new")
        self.status_filter.addItem("In Progress", "in_progress")
        self.status_filter.addItem("Completed", "completed")

        self.status_filter.currentIndexChanged.connect(
            self.refresh_task_list
        )

        self.category_filter = QComboBox()
        self.category_filter.addItem("All categories", "all")
        self.category_filter.addItem(
            "No category",
            "uncategorized"
        )

        self.category_filter.currentIndexChanged.connect(
            self.refresh_task_list
        )

        self.sort_filter = QComboBox()
        self.sort_filter.addItem("Newest first", "newest")
        self.sort_filter.addItem("Title A–Z", "title")
        self.sort_filter.addItem("Deadline soonest", "deadline")
        self.sort_filter.addItem("Importance highest", "importance")
        self.sort_filter.addItem("Urgency highest", "urgency")
        self.sort_filter.addItem("C++ Priority", "priority")

        self.sort_filter.currentIndexChanged.connect(
            self.refresh_task_list
        )

        filters.addWidget(self.status_filter, 1)
        filters.addWidget(self.category_filter, 1)
        filters.addWidget(self.sort_filter, 1)

        filter_layout.addLayout(filters)

        layout.addWidget(filter_panel)

        # =====================================
        # TASK LIST PANEL
        # =====================================

        task_panel = QFrame()
        task_panel.setObjectName("taskListPanel")

        task_layout = QVBoxLayout(task_panel)
        task_layout.setContentsMargins(14, 13, 14, 14)
        task_layout.setSpacing(11)

        # List header
        list_header = QHBoxLayout()

        section_title = QLabel("Your Tasks")
        section_title.setObjectName("sectionTitle")

        self.task_count_label = QLabel("0 tasks")
        self.task_count_label.setObjectName("taskCount")

        list_header.addWidget(section_title)
        list_header.addStretch()
        list_header.addWidget(self.task_count_label)

        task_layout.addLayout(list_header)

        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(8)

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("secondaryButton")
        edit_button.clicked.connect(
            lambda checked=False: self.edit_selected_task()
        )

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(
            lambda checked=False: self.delete_selected_task()
        )

        optimize_button = QPushButton("Optimize Tasks")
        optimize_button.setObjectName("primaryButton")
        optimize_button.clicked.connect(
            lambda checked=False: self.optimize_task_list()
        )

        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()
        actions.addWidget(optimize_button)

        task_layout.addLayout(actions)

        # Actual task list
        self.tasks_list = QListWidget()
        self.tasks_list.setObjectName("tasksList")
        self.tasks_list.setSpacing(4)
        self.tasks_list.setWordWrap(True)

        self.tasks_list.itemDoubleClicked.connect(
            lambda item: self.edit_selected_task(item)
        )

        task_layout.addWidget(self.tasks_list, 1)

        layout.addWidget(task_panel, 1)

        return page

    def build_categories_page(self):
        page = QWidget()
        page.setObjectName("categoriesPage")

        page.setStyleSheet("""
            QWidget#categoriesPage {
                background: transparent;
                color: #F2EAF9;
            }

            QLabel#categoriesEyebrow {
                color: #A58AF5;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QLabel#categoriesTitle {
                color: #F2EAF9;
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#categoriesSubtitle {
                color: #A69AAF;
                font-size: 12px;
            }

            QFrame#categoriesPanel {
                background-color: #1B1624;
                border: 1px solid #352A42;
                border-radius: 14px;
            }

            QLabel#categoriesSectionTitle {
                color: #E9C5DF;
                font-size: 17px;
                font-weight: bold;
            }

            QLabel#categoryCount {
                color: #D6C8F4;
                background-color: #30263B;
                border: 1px solid #493957;
                border-radius: 9px;
                padding: 7px 12px;
                font-weight: bold;
            }

            QListWidget {
                background-color: #15111C;
                color: #F2EAF9;
                border: 1px solid #352A42;
                border-radius: 10px;
                padding: 8px;
                outline: none;
            }

            QListWidget::item {
                background-color: #1D1727;
                padding: 13px;
                margin: 3px;
                border: 1px solid #30263B;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #292136;
                border-color: #57446D;
            }

            QListWidget::item:selected {
                background-color: #392B4D;
                border-color: #A58AF5;
            }

            QPushButton#primaryButton {
                background-color: #A58AF5;
                color: #160F20;
                border: none;
                border-radius: 8px;
                padding: 11px 17px;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #BBA8FA;
            }

            QPushButton#secondaryButton {
                background-color: #30263B;
                color: #D6C8F4;
                border: 1px solid #493957;
                border-radius: 8px;
                padding: 11px 17px;
            }

            QPushButton#secondaryButton:hover {
                background-color: #443653;
            }

            QPushButton#dangerButton {
                background-color: #38202F;
                color: #F2C5DF;
                border: 1px solid #684052;
                border-radius: 8px;
                padding: 11px 17px;
            }

            QPushButton#dangerButton:hover {
                background-color: #553047;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)

        eyebrow = QLabel("TASKFORGE / ORGANIZATION")
        eyebrow.setObjectName("categoriesEyebrow")

        title = QLabel("Categories")
        title.setObjectName("categoriesTitle")

        subtitle = QLabel(
            "Organize your tasks and keep everything structured."
        )
        subtitle.setObjectName("categoriesSubtitle")

        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)

        layout.addLayout(header)

        # Main panel
        panel = QFrame()
        panel.setObjectName("categoriesPanel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 15, 16, 15)
        panel_layout.setSpacing(13)

        # Panel header
        panel_header = QHBoxLayout()

        section_title = QLabel("Your Categories")
        section_title.setObjectName("categoriesSectionTitle")

        self.category_count_label = QLabel("0 categories")
        self.category_count_label.setObjectName("categoryCount")

        panel_header.addWidget(section_title)
        panel_header.addStretch()
        panel_header.addWidget(self.category_count_label)

        panel_layout.addLayout(panel_header)

        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(9)

        add_button = QPushButton("+ Add Category")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(
            lambda checked=False: self.open_add_category()
        )

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("secondaryButton")
        edit_button.clicked.connect(
            lambda checked=False: self.edit_selected_category()
        )

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(
            lambda checked=False: self.delete_selected_category()
        )

        actions.addWidget(add_button)
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addStretch()

        panel_layout.addLayout(actions)

        # Categories list
        self.categories_list = QListWidget()
        self.categories_list.setSpacing(4)

        self.categories_list.itemDoubleClicked.connect(
            lambda item: self.edit_selected_category(item)
        )

        panel_layout.addWidget(self.categories_list, 1)

        layout.addWidget(panel, 1)

        return page

    def build_completed_page(self):
        page = QWidget()
        page.setObjectName("completedPage")

        page.setStyleSheet("""
            QWidget#completedPage {
                background: transparent;
                color: #F2EAF9;
            }

            QLabel#completedEyebrow {
                color: #A58AF5;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QLabel#completedTitle {
                color: #F2EAF9;
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#completedSubtitle {
                color: #A69AAF;
                font-size: 12px;
            }

            QFrame#completedPanel {
                background-color: #1B1624;
                border: 1px solid #352A42;
                border-radius: 14px;
            }

            QLabel#completedSectionTitle {
                color: #D6C8F4;
                font-size: 17px;
                font-weight: bold;
            }

            QLabel#completedCount {
                color: #E9C5DF;
                background-color: #30263B;
                border: 1px solid #493957;
                border-radius: 9px;
                padding: 7px 12px;
                font-weight: bold;
            }

            QListWidget {
                background-color: #15111C;
                color: #F2EAF9;
                border: 1px solid #352A42;
                border-radius: 10px;
                padding: 8px;
                outline: none;
            }

            QListWidget::item {
                background-color: #1D1727;
                color: #E9DFF1;
                padding: 14px;
                margin: 3px;
                border: 1px solid #30263B;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #292136;
                border-color: #57446D;
            }

            QListWidget::item:selected {
                background-color: #392B4D;
                border-color: #A58AF5;
                color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)

        eyebrow = QLabel("TASKFORGE / ACHIEVEMENTS")
        eyebrow.setObjectName("completedEyebrow")

        title = QLabel("Completed Tasks")
        title.setObjectName("completedTitle")

        subtitle = QLabel(
            "Everything you've successfully accomplished."
        )
        subtitle.setObjectName("completedSubtitle")

        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)

        layout.addLayout(header)

        # Main panel
        panel = QFrame()
        panel.setObjectName("completedPanel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 15, 16, 15)
        panel_layout.setSpacing(13)

        # Panel header
        panel_header = QHBoxLayout()

        section_title = QLabel("Your Achievements")
        section_title.setObjectName("completedSectionTitle")

        self.completed_count_label = QLabel("0 completed")
        self.completed_count_label.setObjectName("completedCount")

        panel_header.addWidget(section_title)
        panel_header.addStretch()
        panel_header.addWidget(self.completed_count_label)

        panel_layout.addLayout(panel_header)

        # Completed tasks list
        self.completed_list = QListWidget()
        self.completed_list.setSpacing(4)

        panel_layout.addWidget(self.completed_list, 1)

        layout.addWidget(panel, 1)

        return page

    def switch_page(self, index):
        pages = [
            ("Dashboard", "Your productivity overview"),
            ("My Tasks", "Search, filter and manage your tasks"),
            ("Categories", "Organize tasks with color-coded categories"),
            ("Completed", "Your finished tasks"),
            ("Pomodoro", "Focus on what matters"),
            ("History", "Your completed focus sessions"),
            ("Statistics", "Your productivity insights")
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
    def format_task(task, display_number=None):
        deadline = task[6] or "No deadline"
        status = task[7].replace("_", " ").title()
        title = task[1]

        number = task[0] if display_number is None else display_number

        return (
            f"#{number}   {title}   |   "
            f"{status}   |   Deadline: {deadline}"
        )

    @staticmethod
    def task_is_overdue(task) -> bool:
        return bool(task[6] and task[7] != "completed" and task[6] < date.today().isoformat())

    def refresh_data(self):
        try:
            self.all_tasks = get_tasks()
            self.all_categories = get_categories()
            current_optimizer_source = self._optimizer_signature(
                self.all_tasks
            )

            if (
                    self.optimized_task_source is not None
                    and current_optimizer_source != self.optimized_task_source
            ):
                # Optimization results are no longer valid.
                self.optimized_task_order = {}
                self.optimized_task_priorities = {}
                self.optimized_task_source = None

                # Return to the default sorting mode if C++ priority was selected.
                if self.sort_filter.currentData() == "priority":
                    self.sort_filter.blockSignals(True)
                    self.sort_filter.setCurrentIndex(
                        self.sort_filter.findData("newest")
                    )
                    self.sort_filter.blockSignals(False)

            completed = [task for task in self.all_tasks if task[7] == "completed"]
            in_progress = [task for task in self.all_tasks if task[7] == "in_progress"]
            overdue = [task for task in self.all_tasks if self.task_is_overdue(task)]
            # Calculate overall completion rate.
            completion_rate = (
                round(len(completed) / len(self.all_tasks) * 100)
                if self.all_tasks
                else 0
            )

            self.completion_rate_value.setText(
                f"{completion_rate}%"
            )

            self.completion_progress.setValue(
                completion_rate
            )

            if self.all_tasks:
                self.completion_description.setText(
                    f"{len(completed)} of {len(self.all_tasks)} "
                    "tasks completed."
                )
            else:
                self.completion_description.setText(
                    "Create your first task to get started."
                )

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

            self.category_count_label.setText(
                f"{len(self.all_categories)} "
                f"categor{'y' if len(self.all_categories) == 1 else 'ies'}"
            )

            for category in self.all_categories:
                item = QListWidgetItem(
                    f"{category[1]}   ({category[2]})"
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    category[0]
                )

                # Preserve the user's category color.
                item.setForeground(
                    QBrush(QColor(category[2]))
                )

                self.categories_list.addItem(item)
                item = QListWidgetItem(f"{category[1]}   ({category[2]})")
                item.setData(Qt.ItemDataRole.UserRole, category[0])
                item.setForeground(QBrush(QColor(category[2])))

                self.completed_list.clear()

                self.completed_count_label.setText(
                    f"{len(completed)} completed"
                )

                sorted_completed = sorted(
                    completed,
                    key=lambda row: row[0],
                    reverse=True
                )

                for display_number, task in enumerate(
                        sorted_completed,
                        start=1
                ):
                    item = QListWidgetItem(
                        self.format_task(task, display_number)
                    )

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        task[0]
                    )

                    self.completed_list.addItem(item)

                self.history_page.refresh_data()
                self.statistics_page.refresh_data()

                item = QListWidgetItem(self.format_task(task))
                item.setData(Qt.ItemDataRole.UserRole, task[0])
                self.completed_list.addItem(item)
                self.history_page.refresh_data()
                self.statistics_page.refresh_data()

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

    @staticmethod
    def _optimizer_signature(tasks):
        """
        Build a snapshot of fields that affect C++ optimization.
        """

        return tuple(
            (
                int(task[0]),
                int(task[3]),
                int(task[4]),
                int(task[5]),
                str(task[7]),
            )
            for task in tasks
            if task[7] in {"new", "in_progress"}
        )

    def optimize_task_list(self):
        try:
            # Only unfinished tasks participate in optimization.
            active_tasks = [
                task for task in self.all_tasks
                if task[7] in {"new", "in_progress"}
            ]

            if not active_tasks:
                QMessageBox.information(
                    self,
                    "Task Optimizer",
                    "There are no unfinished tasks to optimize."
                )
                return

            # Send real database tasks to the C++ optimizer.
            optimized_tasks = optimize_task_rows(active_tasks)

            if not optimized_tasks:
                QMessageBox.information(
                    self,
                    "Task Optimizer",
                    "No tasks were returned by the optimizer."
                )
                return

            # Store the optimized order.
            self.optimized_task_order = {
                int(task[0]): index
                for index, task in enumerate(optimized_tasks)
            }

            # Calculate priorities using C++.
            self.optimized_task_priorities = {
                int(task[0]): calculate_task_priority(task)
                for task in optimized_tasks
            }

            self.optimized_task_source = self._optimizer_signature(
                active_tasks
            )

            # Switch the task list to C++ priority sorting.
            priority_index = self.sort_filter.findData("priority")
            self.sort_filter.setCurrentIndex(priority_index)

            self.refresh_task_list()

            QMessageBox.information(
                self,
                "Optimization Complete",
                f"Successfully optimized {len(optimized_tasks)} tasks!"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Optimization Error",
                f"Could not optimize tasks:\n{error}"
            )

    def refresh_task_list(self, *_args):
        if not hasattr(self, "tasks_list"):
            return

        tasks = list(self.all_tasks)

        query = self.search_input.text().strip().casefold()
        status_value = self.status_filter.currentData()
        category_value = self.category_filter.currentData()
        sort_value = self.sort_filter.currentData()

        # Search filter
        if query:
            tasks = [
                task for task in tasks
                if query in (task[1] or "").casefold()
                   or query in (task[2] or "").casefold()
            ]

        # Status filter
        if status_value != "all":
            tasks = [
                task for task in tasks
                if task[7] == status_value
            ]

        # Category filter
        if category_value == "uncategorized":
            tasks = [
                task for task in tasks
                if task[8] is None
            ]

        elif category_value != "all":
            tasks = [
                task for task in tasks
                if task[8] == category_value
            ]
            # Update filtered task counter.
            task_count = len(tasks)

            self.task_count_label.setText(
                f"{task_count} task{'s' if task_count != 1 else ''}"
            )
            # Update filtered task counter
            task_count = len(tasks)

            self.task_count_label.setText(
                f"{task_count} task{'s' if task_count != 1 else ''}"
            )


        # Sorting
        if sort_value == "title":
            tasks.sort(
                key=lambda task: (task[1] or "").casefold()
            )

        elif sort_value == "deadline":
            tasks.sort(
                key=lambda task: (
                    task[6] is None,
                    task[6] or "9999-12-31"
                )
            )

        elif sort_value == "importance":
            tasks.sort(
                key=lambda task: task[3],
                reverse=True
            )

        elif sort_value == "urgency":
            tasks.sort(
                key=lambda task: task[4],
                reverse=True
            )

        elif sort_value == "priority":
            tasks.sort(
                key=lambda task: (
                    task[7] == "completed",
                    self.optimized_task_order.get(
                        task[0],
                        float("inf")
                    )
                )
            )

        else:
            # Newest first
            tasks.sort(
                key=lambda task: task[0],
                reverse=True
            )

        # IMPORTANT: Render the list AFTER sorting,
        # regardless of which sorting option is selected.

        self.tasks_list.clear()

        for display_number, task in enumerate(tasks, start=1):

            task_text = self.format_task(task, display_number)

            if task[0] in self.optimized_task_priorities:
                priority = self.optimized_task_priorities[task[0]]
                task_text += f"   |   Priority: {priority:.2f}"

            item = QListWidgetItem(task_text)
            item.setData(Qt.ItemDataRole.UserRole, task[0])

            if self.task_is_overdue(task):
                item.setForeground(QBrush(QColor("#E9AFCF")))

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
