
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
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
    get_session_stats,
    get_daily_focus_stats,
    get_task_focus_stats
)


# =====================================
# DAILY FOCUS CHART
# =====================================

class DailyFocusChart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = []
        self.setMinimumHeight(260)

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        left = 58
        right = self.width() - 22
        top = 22
        bottom = self.height() - 42

        plot_width = right - left
        plot_height = bottom - top

        if plot_width <= 0 or plot_height <= 0:
            painter.end()
            return

        # Calculate chart scale
        max_seconds = max(
            (item["duration_seconds"] for item in self.data),
            default=0
        )

        max_minutes = max(
            5,
            ((int(max_seconds / 60) + 4) // 5) * 5
        )

        # Draw horizontal grid lines
        painter.setFont(QFont("Segoe UI", 9))

        for i in range(5):

            ratio = i / 4
            y = bottom - ratio * plot_height

            painter.setPen(
                QPen(QColor("#e5e9f0"), 1)
            )

            painter.drawLine(
                left, int(y),
                right, int(y)
            )

            label = f"{int(max_minutes * ratio)}m"

            painter.setPen(QColor("#7b8497"))

            painter.drawText(
                QRectF(3, y - 10, 45, 20),
                Qt.AlignmentFlag.AlignRight |
                Qt.AlignmentFlag.AlignVCenter,
                label
            )

        # Draw bars
        count = len(self.data)

        if count == 0:
            painter.end()
            return

        slot_width = plot_width / count
        bar_width = min(42, slot_width * 0.55)

        for i, item in enumerate(self.data):

            seconds = item["duration_seconds"]
            minutes = seconds / 60

            bar_height = (
                minutes / max_minutes
            ) * plot_height

            x = (
                left
                + i * slot_width
                + (slot_width - bar_width) / 2
            )

            y = bottom - bar_height

            if seconds > 0:

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor("#3658d4"))

                painter.drawRoundedRect(
                    QRectF(
                        x,
                        y,
                        bar_width,
                        max(bar_height, 3)
                    ),
                    6,
                    6
                )

                # Duration above bar
                painter.setPen(QColor("#3658d4"))
                painter.setFont(
                    QFont("Segoe UI", 8, QFont.Weight.Bold)
                )

                painter.drawText(
                    QRectF(
                        x - 12,
                        y - 23,
                        bar_width + 24,
                        19
                    ),
                    Qt.AlignmentFlag.AlignCenter,
                    f"{minutes:.0f}m"
                )

            # Day labels
            day_label = item["date"][5:]

            painter.setPen(QColor("#7b8497"))
            painter.setFont(QFont("Segoe UI", 9))

            painter.drawText(
                QRectF(
                    left + i * slot_width,
                    bottom + 10,
                    slot_width,
                    25
                ),
                Qt.AlignmentFlag.AlignCenter,
                day_label
            )

        painter.end()


# =====================================
# STATISTICS WIDGET
# =====================================

class StatisticsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("statisticsPage")

        self.setup_ui()
        self.refresh_data()

    # =====================================
    # UI
    # =====================================

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget#statisticsPage {
                background-color: #f4f6fa;
                color: #20283a;
                font-family: "Segoe UI";
            }

            QFrame#statCard {
                background-color: white;
                border: 1px solid #e5e9f0;
                border-radius: 12px;
            }

            QLabel#statTitle {
                color: #7b8497;
                font-size: 13px;
            }

            QLabel#statValue {
                color: #172033;
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#sectionTitle {
                color: #172033;
                font-size: 17px;
                font-weight: bold;
            }

            QListWidget {
                background-color: white;
                border: 1px solid #e5e9f0;
                border-radius: 10px;
                padding: 8px;
            }

            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f2f6;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 0)
        main_layout.setSpacing(18)

        # Statistics cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        card, self.total_focus_value = self.make_stat_card(
            "Total Focus Time"
        )
        cards_layout.addWidget(card)

        card, self.total_sessions_value = self.make_stat_card(
            "Completed Sessions"
        )
        cards_layout.addWidget(card)

        card, self.average_value = self.make_stat_card(
            "Average Session"
        )
        cards_layout.addWidget(card)

        card, self.week_value = self.make_stat_card(
            "Last 7 Days"
        )
        cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

        # Weekly chart
        chart_title = QLabel("Focus Time — Last 7 Days")
        chart_title.setObjectName("sectionTitle")

        main_layout.addWidget(chart_title)

        chart_card = QFrame()
        chart_card.setObjectName("statCard")

        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(15, 15, 15, 10)

        self.daily_chart = DailyFocusChart()
        chart_layout.addWidget(self.daily_chart)

        main_layout.addWidget(chart_card)

        # Top tasks
        tasks_title = QLabel("Most Focused Tasks")
        tasks_title.setObjectName("sectionTitle")

        main_layout.addWidget(tasks_title)

        self.top_tasks_list = QListWidget()
        self.top_tasks_list.setMaximumHeight(180)

        main_layout.addWidget(self.top_tasks_list)

        main_layout.addStretch()

    # =====================================
    # STATISTIC CARD
    # =====================================

    @staticmethod
    def make_stat_card(title):

        card = QFrame()
        card.setObjectName("statCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 16, 15, 16)
        layout.setSpacing(10)

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
            return f"{minutes} min"

        return f"{remaining_seconds} sec"

    # =====================================
    # REFRESH STATISTICS
    # =====================================

    def refresh_data(self):

        try:
            # Get statistics from repository
            stats = get_session_stats()

            daily_stats = get_daily_focus_stats(days=7)

            task_stats = get_task_focus_stats(limit=5)

            weekly_seconds = sum(
                item["duration_seconds"]
                for item in daily_stats
            )

            # Update summary cards
            self.total_focus_value.setText(
                self.format_duration(stats["total_seconds"])
            )

            self.total_sessions_value.setText(
                str(stats["total_sessions"])
            )

            self.average_value.setText(
                self.format_duration(stats["average_seconds"])
            )

            self.week_value.setText(
                self.format_duration(weekly_seconds)
            )

            # Update chart
            self.daily_chart.set_data(daily_stats)

            # Update top tasks
            self.top_tasks_list.clear()

            if not task_stats:

                self.top_tasks_list.addItem(
                    "No completed focus sessions yet."
                )

            else:

                for index, task in enumerate(task_stats, start=1):

                    title = task["task_title"]
                    duration = self.format_duration(
                        task["duration_seconds"]
                    )

                    sessions = task["sessions"]

                    item = QListWidgetItem(
                        f"{index}.  {title}   |   "
                        f"{duration}   |   "
                        f"{sessions} sessions"
                    )

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        task["task_id"]
                    )

                    self.top_tasks_list.addItem(item)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Statistics Error",
                f"Could not load statistics:\n{error}"
            )
