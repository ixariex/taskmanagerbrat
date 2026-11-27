from datetime import date

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ui.styles import PAGE_COMMON_STYLESHEET, create_stat_card


class DashboardWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardPage")
        self.setStyleSheet(PAGE_COMMON_STYLESHEET + """
            QWidget#dashboardPage {
                background-color: #100D16;
                color: #F2EAF9;
            }
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        header = QVBoxLayout()
        header.setSpacing(4)
        eyebrow = QLabel("TASKFORGE / YOUR WORKSPACE")
        eyebrow.setObjectName("pageEyebrow")
        title = QLabel("Welcome back.")
        title.setObjectName("heroTitle")
        subtitle = QLabel("Here's your productivity overview.")
        subtitle.setObjectName("heroSubtitle")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Statistics Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(13)
        card, self.total_value = create_stat_card("Total Tasks")
        cards_layout.addWidget(card)
        card, self.progress_value = create_stat_card("In Progress")
        cards_layout.addWidget(card)
        card, self.completed_value = create_stat_card("Completed")
        cards_layout.addWidget(card)
        card, self.overdue_value = create_stat_card("Overdue")
        cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        # Bottom Section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

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
        rate_label.setObjectName("heroSubtitle")
        self.completion_rate_value = QLabel("0%")
        self.completion_rate_value.setStyleSheet(
            "color: #D6C8F4; font-size: 22px; font-weight: bold; background: transparent;"
        )
        rate_header.addWidget(rate_label)
        rate_header.addStretch()
        rate_header.addWidget(self.completion_rate_value)
        overview_layout.addLayout(rate_header)

        self.completion_progress = QProgressBar()
        self.completion_progress.setRange(0, 100)
        self.completion_progress.setValue(0)
        self.completion_progress.setTextVisible(False)
        self.completion_progress.setFixedHeight(9)
        overview_layout.addWidget(self.completion_progress)

        self.completion_description = QLabel("Complete your first task to get started.")
        self.completion_description.setWordWrap(True)
        self.completion_description.setObjectName("heroSubtitle")
        overview_layout.addWidget(self.completion_description)
        overview_layout.addStretch()
        bottom_layout.addWidget(overview_card, 1)

        # Recent Tasks Card
        recent_card = QFrame()
        recent_card.setObjectName("statCard")
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(20, 18, 20, 18)
        recent_layout.setSpacing(12)

        recent_header = QHBoxLayout()
        recent_title = QLabel("Recent Tasks")
        recent_title.setObjectName("sectionTitle")
        recent_subtitle = QLabel("Your latest activity")
        recent_subtitle.setObjectName("heroSubtitle")
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

    @staticmethod
    def _is_overdue(task) -> bool:
        return bool(task[6] and task[7] != "completed" and task[6] < date.today().isoformat())

    @staticmethod
    def _format_task(task, display_number: int) -> str:
        deadline = task[6] or "No deadline"
        status = task[7].replace("_", " ").title()
        return f"#{display_number}   {task[1]}   |   {status}   |   Deadline: {deadline}"

    def refresh_data(self, tasks: list) -> None:
        completed = [t for t in tasks if t[7] == "completed"]
        in_progress = [t for t in tasks if t[7] == "in_progress"]
        overdue = [t for t in tasks if self._is_overdue(t)]

        completion_rate = round(len(completed) / len(tasks) * 100) if tasks else 0
        self.completion_rate_value.setText(f"{completion_rate}%")
        self.completion_progress.setValue(completion_rate)

        if tasks:
            self.completion_description.setText(f"{len(completed)} of {len(tasks)} tasks completed.")
        else:
            self.completion_description.setText("Create your first task to get started.")

        self.total_value.setText(str(len(tasks)))
        self.progress_value.setText(str(len(in_progress)))
        self.completed_value.setText(str(len(completed)))
        self.overdue_value.setText(str(len(overdue)))

        self.recent_list.clear()
        recent_tasks = sorted(tasks, key=lambda row: row[0], reverse=True)[:5]
        for number, task in enumerate(recent_tasks, start=1):
            self.recent_list.addItem(self._format_task(task, number))
