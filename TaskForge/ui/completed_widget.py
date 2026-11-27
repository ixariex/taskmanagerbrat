from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.styles import PAGE_COMMON_STYLESHEET


class CompletedWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("completedPage")
        self.setStyleSheet(PAGE_COMMON_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        header = QVBoxLayout()
        header.setSpacing(4)
        eyebrow = QLabel("TASKFORGE / ACHIEVEMENTS")
        eyebrow.setObjectName("pageEyebrow")
        title = QLabel("Completed Tasks")
        title.setObjectName("heroTitle")
        subtitle = QLabel("Everything you've successfully accomplished.")
        subtitle.setObjectName("heroSubtitle")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        panel = QFrame()
        panel.setObjectName("contentPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 15, 16, 15)
        panel_layout.setSpacing(13)

        panel_header = QHBoxLayout()
        section_title = QLabel("Your Achievements")
        section_title.setObjectName("sectionTitle")
        self.completed_count_label = QLabel("0 completed")
        self.completed_count_label.setObjectName("countBadge")
        panel_header.addWidget(section_title)
        panel_header.addStretch()
        panel_header.addWidget(self.completed_count_label)
        panel_layout.addLayout(panel_header)

        self.completed_list = QListWidget()
        self.completed_list.setObjectName("cardList")
        self.completed_list.setSpacing(4)
        panel_layout.addWidget(self.completed_list, 1)

        layout.addWidget(panel, 1)

    @staticmethod
    def _format_task(task, display_number: int) -> str:
        deadline = task[6] or "No deadline"
        status = task[7].replace("_", " ").title()
        return f"#{display_number}   {task[1]}   |   {status}   |   Deadline: {deadline}"

    def refresh_data(self, tasks: list) -> None:
        completed = [t for t in tasks if t[7] == "completed"]
        self.completed_list.clear()
        self.completed_count_label.setText(f"{len(completed)} completed")

        sorted_completed = sorted(completed, key=lambda row: row[0], reverse=True)
        for display_number, task in enumerate(sorted_completed, start=1):
            item = QListWidgetItem(self._format_task(task, display_number))
            item.setData(Qt.ItemDataRole.UserRole, task[0])
            self.completed_list.addItem(item)
