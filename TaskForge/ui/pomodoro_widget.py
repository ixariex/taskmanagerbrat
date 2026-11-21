
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFrame
)


class PomodoroWidget(QWidget):

    WORK_SECONDS = 25 * 60
    SHORT_BREAK_SECONDS = 5 * 60
    LONG_BREAK_SECONDS = 15 * 60


    def __init__(self, parent=None):
        super().__init__(parent)

        # Timer state
        self.mode = "work"
        self.remaining_seconds = self.WORK_SECONDS
        self.completed_work_sessions = 0
        self.is_running = False

        # Qt timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self.setup_ui()
        self.update_display()

    # =====================================
    # UI
    # =====================================

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6fa;
                color: #20283a;
                font-family: "Segoe UI";
            }

            QFrame#timerCard {
                background-color: white;
                border: 1px solid #e5e9f0;
                border-radius: 18px;
            }

            QLabel#timerTitle {
                font-size: 24px;
                font-weight: bold;
                color: #172033;
            }

            QLabel#modeLabel {
                font-size: 15px;
                font-weight: bold;
                color: #3658d4;
            }

            QLabel#timerDisplay {
                font-size: 76px;
                font-weight: bold;
                color: #172033;
            }

            QLabel#sessionLabel {
                font-size: 14px;
                color: #7b8497;
            }

            QLabel#messageLabel {
                font-size: 13px;
                color: #64748b;
            }

            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #e8edf5;
                height: 10px;
            }

            QProgressBar::chunk {
                background-color: #3658d4;
                border-radius: 5px;
            }

            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#startButton {
                background-color: #3658d4;
                color: white;
            }

            QPushButton#startButton:hover {
                background-color: #2948b8;
            }

            QPushButton#resetButton {
                background-color: #e9edf5;
                color: #26334d;
            }

            QPushButton#resetButton:hover {
                background-color: #dbe2ee;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Timer card
        card = QFrame()
        card.setObjectName("timerCard")
        card.setMaximumWidth(650)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(45, 40, 45, 40)
        card_layout.setSpacing(20)

        # Title
        title = QLabel("Pomodoro Timer")
        title.setObjectName("timerTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title)

        # Current mode
        self.mode_label = QLabel()
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.mode_label)

        # Digital timer
        self.timer_display = QLabel()
        self.timer_display.setObjectName("timerDisplay")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.timer_display)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)

        card_layout.addWidget(self.progress_bar)

        # Sessions
        self.session_label = QLabel()
        self.session_label.setObjectName("sessionLabel")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.session_label)

        # Information
        self.message_label = QLabel(
            "Stay focused. One task at a time."
        )
        self.message_label.setObjectName("messageLabel")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.message_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.toggle_timer)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self.reset_timer)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.reset_button)

        card_layout.addLayout(buttons_layout)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    # =====================================
    # TIMER LOGIC
    # =====================================

    def get_current_duration(self):

        if self.mode == "work":
            return self.WORK_SECONDS

        if self.mode == "short_break":
            return self.SHORT_BREAK_SECONDS

        return self.LONG_BREAK_SECONDS

    def toggle_timer(self):

        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):

        if self.remaining_seconds <= 0:
            return

        self.timer.start()
        self.is_running = True

        self.start_button.setText("Pause")
        self.message_label.setText("You are doing great. Keep going!")

    def pause_timer(self):

        self.timer.stop()
        self.is_running = False

        self.start_button.setText("Resume")
        self.message_label.setText("Timer paused.")

    def reset_timer(self):

        self.timer.stop()
        self.is_running = False

        self.remaining_seconds = self.get_current_duration()

        self.start_button.setText("Start")
        self.message_label.setText("Timer reset.")

        self.update_display()

    def _on_tick(self):

        self.remaining_seconds -= 1

        if self.remaining_seconds <= 0:

            self.timer.stop()
            self.is_running = False

            self.finish_phase()

        self.update_display()



    def finish_phase(self):

        self.start_button.setText("Start")

        if self.mode == "work":

            self.completed_work_sessions += 1

            if (
                self.completed_work_sessions
            ):
                self.mode = "long_break"
                self.message_label.setText(
                    "Great work! Time for a long break."
                )
            else:
                self.mode = "short_break"
                self.message_label.setText(
                    "Focus session completed! Take a break."
                )

        else:

            self.mode = "work"
            self.message_label.setText(
                "Break completed. Ready to focus again?"
            )

        self.remaining_seconds = self.get_current_duration()


    def update_display(self):

        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60

        self.timer_display.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        if self.mode == "work":
            self.mode_label.setText("FOCUS SESSION")

        elif self.mode == "short_break":
            self.mode_label.setText("SHORT BREAK")

        else:
            self.mode_label.setText("LONG BREAK")

        self.session_label.setText(
            f"Completed focus sessions: "
            f"{self.completed_work_sessions}"

        )

        self.progress_bar.setMaximum(
            self.get_current_duration()
        )

        self.progress_bar.setValue(
            self.remaining_seconds
        )
