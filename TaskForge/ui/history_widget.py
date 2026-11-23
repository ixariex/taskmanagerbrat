
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QMessageBox
)

from database.pomodoro_repository import (
    get_all_sessions,
    get_session_stats
)


class HistoryWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("historyPage")

        self.setup_ui()
        self.refresh_data()

    # =====================================
    # UI
    # =====================================

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget#historyPage {
                background-color: #100D16;
                color: #F2EAF9;
                font-family: "Segoe UI";
            }

            QLabel#historyEyebrow {
                color: #A58AF5;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QLabel#historyTitle {
                color: #F2EAF9;
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#historySubtitle {
                color: #A69AAF;
                font-size: 12px;
            }

            QFrame#historyStatCard {
                background-color: #1B1624;
                border: 1px solid #3A2D48;
                border-radius: 13px;
            }

            QFrame#historyStatCard:hover {
                border: 1px solid #725A91;
                background-color: #211A2D;
            }

            QLabel#statTitle {
                color: #A69AAF;
                font-size: 12px;
            }

            QLabel#statValue {
                color: #D6C8F4;
                font-size: 23px;
                font-weight: bold;
            }

            QFrame#historyPanel {
                background-color: #1B1624;
                border: 1px solid #3A2D48;
                border-radius: 14px;
            }

            QLabel#historySectionTitle {
                font-size: 17px;
                font-weight: bold;
                color: #E9C5DF;
            }

            QLabel#historyCount {
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
                color: #E9DFF1;
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

            QScrollBar:vertical {
                background-color: #15111C;
                width: 9px;
                margin: 3px;
                border: none;
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
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)

        eyebrow = QLabel("TASKFORGE / PRODUCTIVITY")
        eyebrow.setObjectName("historyEyebrow")

        title = QLabel("Focus History")
        title.setObjectName("historyTitle")

        subtitle = QLabel(
            "Review your completed focus sessions and track your progress."
        )
        subtitle.setObjectName("historySubtitle")

        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)

        main_layout.addLayout(header)

        # Statistics cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        card, self.total_sessions_value = self.make_stat_card(
            "Total Sessions"
        )
        cards_layout.addWidget(card)

        card, self.total_focus_value = self.make_stat_card(
            "Total Focus Time"
        )
        cards_layout.addWidget(card)

        card, self.today_sessions_value = self.make_stat_card(
            "Today's Sessions"
        )
        cards_layout.addWidget(card)

        card, self.today_focus_value = self.make_stat_card(
            "Today's Focus Time"
        )
        cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

        # History panel
        panel = QFrame()
        panel.setObjectName("historyPanel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 15, 16, 15)
        panel_layout.setSpacing(13)

        section_header = QHBoxLayout()

        section_title = QLabel("Completed Focus Sessions")
        section_title.setObjectName("historySectionTitle")

        self.history_count_label = QLabel("0 sessions")
        self.history_count_label.setObjectName("historyCount")

        section_header.addWidget(section_title)
        section_header.addStretch()
        section_header.addWidget(self.history_count_label)

        panel_layout.addLayout(section_header)

        self.sessions_list = QListWidget()
        self.sessions_list.setSpacing(4)
        self.sessions_list.setAlternatingRowColors(False)

        panel_layout.addWidget(self.sessions_list, 1)

        main_layout.addWidget(panel, 1)

    # =====================================
    # STATISTICS CARD
    # =====================================

    @staticmethod
    def make_stat_card(title):

        card = QFrame()
        card.setObjectName("historyStatCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 14, 15, 14)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_label = QLabel("0")
        value_label.setObjectName("statValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card, value_label

    # =====================================
    # FORMATTING
    # =====================================

    @staticmethod
    def format_duration(seconds):

        seconds = int(seconds)

        hours, remainder = divmod(seconds, 3600)
        minutes, remaining_seconds = divmod(remainder, 60)

        if hours:
            return f"{hours} h {minutes} min"

        if minutes:
            if remaining_seconds:
                return f"{minutes} min {remaining_seconds} sec"

            return f"{minutes} min"

        return f"{remaining_seconds} sec"

    @staticmethod
    def format_datetime(value):

        try:
            timestamp = datetime.fromisoformat(value)

            if timestamp.tzinfo is not None:
                timestamp = timestamp.astimezone()

            return timestamp.strftime("%d.%m.%Y %H:%M")

        except (ValueError, TypeError):
            return str(value)

    # =====================================
    # REFRESH HISTORY
    # =====================================

    def refresh_data(self):

        try:
            sessions = get_all_sessions()
            stats = get_session_stats()

            today = datetime.now().astimezone().date()

            today_sessions = []

            for session in sessions:

                completed_at = datetime.fromisoformat(
                    session[4]
                )

                if completed_at.tzinfo is not None:
                    completed_at = completed_at.astimezone()

                if completed_at.date() == today:
                    today_sessions.append(session)

            today_seconds = sum(
                session[5]
                for session in today_sessions
            )

            # Update statistics
            self.total_sessions_value.setText(
                str(stats["total_sessions"])
            )

            self.total_focus_value.setText(
                self.format_duration(stats["total_seconds"])
            )

            self.today_sessions_value.setText(
                str(len(today_sessions))
            )

            self.today_focus_value.setText(
                self.format_duration(today_seconds)
            )

            # Update history list
            self.sessions_list.clear()

            self.history_count_label.setText(
                f"{len(sessions)} sessions"
            )

            if not sessions:

                item = QListWidgetItem(
                    "No completed focus sessions yet."
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.sessions_list.addItem(item)
                return

            for session in sessions:

                session_id = session[0]
                task_id = session[1]
                task_title = session[2]
                completed_at = session[4]
                duration_seconds = session[5]

                formatted_date = self.format_datetime(
                    completed_at
                )

                formatted_duration = self.format_duration(
                    duration_seconds
                )

                if task_id is None:
                    task_info = f"{task_title} (task deleted)"
                else:
                    task_info = task_title

                item = QListWidgetItem(
                    f"{formatted_date}   |   "
                    f"{task_info}   |   "
                    f"{formatted_duration}"
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    session_id
                )

                self.sessions_list.addItem(item)

        except Exception as error:

            QMessageBox.critical(
                self,
                "History Error",
                f"Could not load session history:\n{error}"
            )
