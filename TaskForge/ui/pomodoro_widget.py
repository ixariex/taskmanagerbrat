
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFrame,
    QComboBox
)

from core.task_manager import get_tasks
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox

from database.pomodoro_repository import add_completed_session


class PomodoroWidget(QWidget):

    WORK_SECONDS = 10
    SHORT_BREAK_SECONDS = 5
    LONG_BREAK_SECONDS = 15

    SESSIONS_BEFORE_LONG_BREAK = 4

    def __init__(self, parent=None):
        super().__init__(parent)

        # Timer state
        self.mode = "work"
        self.remaining_seconds = self.WORK_SECONDS
        self.completed_work_sessions = 0
        self.is_running = False

        # Selected task
        self.selected_task_id = None
        # Active work session
        self.session_task_id = None
        self.session_task_title = None
        self.session_started_at = None
        self.session_elapsed_seconds = 0

        # Qt timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self.setup_ui()
        self.refresh_tasks()
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

            QComboBox {
                background-color: #f8f9fc;
                border: 1px solid #dce2ec;
                border-radius: 8px;
                padding: 10px;
                min-width: 220px;
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

        # Main card
        card = QFrame()
        card.setObjectName("timerCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(45, 40, 45, 40)
        card_layout.setSpacing(20)

        # Title
        title = QLabel("TaskForge Timer")
        title.setObjectName("timerTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Task selection
        task_title = QLabel("CURRENT TASK")
        task_title.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #7b8497;
        """)
        card_layout.addWidget(task_title)

        task_layout = QHBoxLayout()

        self.task_selector = QComboBox()
        self.task_selector.setMinimumWidth(260)
        self.task_selector.currentIndexChanged.connect(
            self.on_task_changed
        )

        self.refresh_tasks_button = QPushButton("Refresh")
        self.refresh_tasks_button.setObjectName("resetButton")
        self.refresh_tasks_button.clicked.connect(
            lambda: self.refresh_tasks()
        )

        task_layout.addWidget(self.task_selector)
        task_layout.addWidget(self.refresh_tasks_button)

        card_layout.addLayout(task_layout)

        # Selected task information
        self.task_info = QLabel("No task selected")
        self.task_info.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.task_info.setStyleSheet(
            "color: #7b8497; font-size: 12px;"
        )

        card_layout.addWidget(self.task_info)

        # Mode
        self.mode_label = QLabel()
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(self.mode_label)

        # Digital timer
        self.timer_display = QLabel()
        self.timer_display.setObjectName("timerDisplay")
        self.timer_display.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(self.timer_display)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)

        card_layout.addWidget(self.progress_bar)

        # Completed sessions
        self.session_label = QLabel()
        self.session_label.setObjectName("sessionLabel")
        self.session_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(self.session_label)

        # Message
        self.message_label = QLabel(
            "Select a task and start focusing."
        )
        self.message_label.setObjectName("messageLabel")
        self.message_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(self.message_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(
            self.toggle_timer
        )

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(
            self.reset_timer
        )

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.reset_button)

        card_layout.addLayout(buttons_layout)

        main_layout.addWidget(
            card,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

    # =====================================
    # TASK SELECTION
    # =====================================

    def refresh_tasks(self):

        # Preserve current selection
        current_id = self.task_selector.currentData()

        self.task_selector.blockSignals(True)
        self.task_selector.clear()

        self.task_selector.addItem(
            "Select a task...",
            None
        )

        try:
            tasks = get_tasks()

            for task in tasks:

                task_id = task[0]
                title = task[1]
                status = task[7]

                # Do not show completed tasks
                if status == "completed":
                    continue

                self.task_selector.addItem(
                    title,
                    task_id
                )

            index = self.task_selector.findData(
                current_id
            )

            if index >= 0:
                self.task_selector.setCurrentIndex(index)
            else:
                self.task_selector.setCurrentIndex(0)

            self.task_selector.blockSignals(False)
            self.on_task_changed()

        except Exception as error:

            self.task_selector.blockSignals(False)

            self.selected_task_id = None

            self.task_info.setText(
                f"Could not load tasks: {error}"
            )

    def on_task_changed(self, *_args):

        task_id = self.task_selector.currentData()

        self.selected_task_id = task_id

        if task_id is None:

            self.task_info.setText(
                "Select a task before starting."
            )

        else:

            task_name = self.task_selector.currentText()

            self.task_info.setText(
                f"Working on: {task_name}"
            )

    def get_selected_task_id(self):

        return self.selected_task_id

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

        # Work session requires a selected task
        if self.mode == "work":

            if self.selected_task_id is None:
                self.message_label.setText(
                    "Please select a task first."
                )
                return

            # Create session data only on the first start.
            # Resume must not reset the start time or elapsed time.
            if self.session_started_at is None:
                self.session_task_id = self.selected_task_id
                self.session_task_title = self.task_selector.currentText()

                self.session_started_at = (
                    datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds")
                )

                self.session_elapsed_seconds = 0

        if self.remaining_seconds <= 0:
            return

        self.timer.start()
        self.is_running = True

        self.task_selector.setEnabled(False)
        self.refresh_tasks_button.setEnabled(False)

        self.start_button.setText("Pause")

        self.message_label.setText(
            "Stay focused. Keep going!"
        )

    def pause_timer(self):

        self.timer.stop()
        self.is_running = False

        self.start_button.setText("Resume")

        self.message_label.setText(
            "Timer paused."
        )

    def reset_timer(self):

        self.timer.stop()
        self.is_running = False

        # Reset an unfinished work session
        if self.mode == "work":
            self.clear_active_session()

        self.remaining_seconds = self.get_current_duration()

        self.task_selector.setEnabled(True)
        self.refresh_tasks_button.setEnabled(True)

        self.start_button.setText("Start")

        self.message_label.setText(
            "Timer reset."
        )

        self.update_display()

    def _on_tick(self):

        self.remaining_seconds -= 1

        # Count only actual focus time
        if self.mode == "work" and self.session_started_at is not None:
            self.session_elapsed_seconds += 1

        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0

            self.timer.stop()
            self.is_running = False

            self.finish_phase()

        self.update_display()

    # =====================================
    # PHASE MANAGEMENT
    # =====================================

    def save_completed_session(self):

        if (
                self.session_task_id is None
                or self.session_started_at is None
                or self.session_elapsed_seconds <= 0
        ):
            self.clear_active_session()
            return False

        completed_at = (
            datetime.now()
            .astimezone()
            .isoformat(timespec="seconds")
        )

        try:
            add_completed_session(
                task_id=self.session_task_id,
                task_title=self.session_task_title,
                started_at=self.session_started_at,
                completed_at=completed_at,
                duration_seconds=self.session_elapsed_seconds
            )

            print("POMODORO SESSION SAVED")

            self.clear_active_session()
            return True

        except Exception as error:
            QMessageBox.warning(
                self,
                "Session History Error",
                f"Could not save session:\n{error}"
            )

            self.clear_active_session()
            return False

    def clear_active_session(self):

        self.session_task_id = None
        self.session_task_title = None
        self.session_started_at = None
        self.session_elapsed_seconds = 0

    def finish_phase(self):

        self.start_button.setText("Start")

        self.task_selector.setEnabled(True)
        self.refresh_tasks_button.setEnabled(True)

        if self.mode == "work":

            # Save completed work session
            session_saved = self.save_completed_session()

            self.completed_work_sessions += 1

            if (
                    self.completed_work_sessions
                    % self.SESSIONS_BEFORE_LONG_BREAK == 0
            ):

                self.mode = "long_break"

                if session_saved:
                    self.message_label.setText(
                        "Session saved! Time for a long break."
                    )
                else:
                    self.message_label.setText(
                        "Session completed, but history was not saved."
                    )

            else:

                self.mode = "short_break"

                if session_saved:
                    self.message_label.setText(
                        "Session saved! Take a short break."
                    )
                else:
                    self.message_label.setText(
                        "Session completed, but history was not saved."
                    )

        else:

            self.mode = "work"

            self.message_label.setText(
                "Break completed. Ready to focus again?"
            )

        self.remaining_seconds = self.get_current_duration()

        # Select a task again before the next work session
        if self.mode == "work":
            self.selected_task_id = None
            self.task_selector.setCurrentIndex(0)

        self.update_display()

    # =====================================
    # DISPLAY UPDATE
    # =====================================

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
