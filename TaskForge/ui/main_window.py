from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.category_manager import get_categories
from core.settings_manager import load_settings, save_settings
from core.task_manager import create_task, get_tasks
from core.theme_manager import transform_stylesheet
from ui.categories_widget import CategoriesWidget
from ui.completed_widget import CompletedWidget
from ui.dashboard_widget import DashboardWidget
from ui.history_widget import HistoryWidget
from ui.pomodoro_widget import PomodoroWidget
from ui.settings_widget import SettingsWidget
from ui.silent_message_box import SilentMessageBox as QMessageBox
from ui.statistics_widget import StatisticsWidget
from ui.styles import APP_STYLESHEET
from ui.task_dialog import TaskDialog
from ui.tasks_widget import TasksWidget


class MainWindow(QMainWindow):
    PAGES: list[tuple[str, str, str]] = [
        ("Dashboard", "Dashboard", "Your productivity overview"),
        ("My Tasks", "My Tasks", "Search, filter and manage your tasks"),
        ("Categories", "Categories", "Organize tasks with color-coded categories"),
        ("Completed", "Completed", "Your finished tasks"),
        ("Timer", "Pomodoro", "Focus on what matters"),
        ("History", "History", "Your completed focus sessions"),
        ("Statistics", "Statistics", "Your productivity insights"),
        ("Settings", "Settings", "Personalize your TaskForge workspace"),
    ]
    TASK_CREATION_PAGES = {0, 1}

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TaskForge")
        self.resize(1180, 780)
        self.setMinimumSize(950, 620)
        self.settings = load_settings()
        self.setStyleSheet(APP_STYLESHEET)

        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._create_sidebar(root_layout)
        self._create_content(root_layout)

        self.tasks_page.tasksChanged.connect(self.refresh_data)
        self.categories_page.categoriesChanged.connect(self.refresh_data)
        self.settings_page.settingsChanged.connect(self.on_settings_changed)

        self.apply_visual_settings(self.settings)
        self.switch_page(0)

    # ---------- Theme & Settings ----------
    def on_settings_changed(self, settings: dict) -> None:
        try:
            self.settings = save_settings(settings)
            self.apply_visual_settings(self.settings)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Settings Could Not Be Saved",
                f"Your appearance was changed, but the settings file could not be saved:\n{error}",
            )

    def apply_visual_settings(self, settings: dict | None = None) -> None:
        settings = settings or self.settings
        theme = settings.get("theme", "dark")
        accent = settings.get("accent_color", "#A58AF5")
        text_scale = settings.get("text_scale", "medium")
        custom_colors = settings.get("custom_colors")

        for widget in [self] + self.findChildren(QWidget):
            if widget.property("_taskforge_skip_theme"):
                continue

            original = widget.property("_taskforge_original_stylesheet")
            if original is None:
                original = widget.styleSheet()
                widget.setProperty("_taskforge_original_stylesheet", original)

            if original:
                widget.setStyleSheet(
                    transform_stylesheet(
                        original,
                        theme,
                        accent,
                        text_scale,
                        custom_colors=custom_colors,
                    )
                )

    # ---------- Layout ----------
    def _create_sidebar(self, root_layout: QHBoxLayout) -> None:
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

        self.nav_buttons: list[QPushButton] = []
        for index, (nav_label, _, _) in enumerate(self.PAGES):
            button = QPushButton(f"   {nav_label}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda _=False, i=index: self.switch_page(i))
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch()
        version = QLabel("TaskForge v1.1")
        version.setObjectName("sidebarSubtitle")
        layout.addWidget(version)
        root_layout.addWidget(sidebar)

    def _create_content(self, root_layout: QHBoxLayout) -> None:
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
        self.add_task_button.clicked.connect(self.open_add_task)
        header.addWidget(self.add_task_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.clicked.connect(self.refresh_data)
        header.addWidget(refresh_button)
        layout.addLayout(header)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardWidget()
        self.tasks_page = TasksWidget()
        self.categories_page = CategoriesWidget()
        self.completed_page = CompletedWidget()
        self.pomodoro_page = PomodoroWidget()
        self.history_page = HistoryWidget()
        self.statistics_page = StatisticsWidget()
        self.settings_page = SettingsWidget(self.settings)

        for page in (
            self.dashboard_page,
            self.tasks_page,
            self.categories_page,
            self.completed_page,
            self.pomodoro_page,
            self.history_page,
            self.statistics_page,
            self.settings_page,
        ):
            self.stack.addWidget(page)

        layout.addWidget(self.stack)
        root_layout.addWidget(content)

    # ---------- Navigation & Data ----------
    def switch_page(self, index: int) -> None:
        if not (0 <= index < len(self.PAGES)):
            return

        _, title, subtitle = self.PAGES[index]
        self.stack.setCurrentIndex(index)
        self.page_title.setText(title)
        self.page_subtitle.setText(subtitle)

        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

        self.add_task_button.setVisible(index in self.TASK_CREATION_PAGES)
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            tasks = get_tasks()
            categories = get_categories()

            self.dashboard_page.refresh_data(tasks)
            self.tasks_page.refresh_data(tasks, categories)
            self.categories_page.refresh_data(categories)
            self.completed_page.refresh_data(tasks)
            self.history_page.refresh_data()
            self.statistics_page.refresh_data()
        except Exception as error:
            QMessageBox.critical(self, "Loading Error", f"Could not load data:\n{error}")

    def open_add_task(self) -> None:
        dialog = TaskDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            create_task(**dialog.get_data())
            self.refresh_data()
            QMessageBox.information(self, "Success", "Task created successfully!")
        except Exception as error:
            QMessageBox.critical(self, "Create Error", str(error))
