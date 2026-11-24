
from datetime import datetime

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFrame,
    QComboBox,
    QSizePolicy,
)

from core.task_manager import get_tasks
from database.pomodoro_repository import add_completed_session
from ui.silent_message_box import SilentMessageBox as QMessageBox


class PomodoroWidget(QWidget):

    WORK_SECONDS = 25 * 60
    SHORT_BREAK_SECONDS = 5 * 60
    LONG_BREAK_SECONDS = 15 * 60

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

        self.setObjectName("pomodoroPage")

        self.setStyleSheet("""
            QWidget#pomodoroPage {
                background-color: #100D16;
                color: #F2EAF9;
                font-family: "Segoe UI";
            }

            QFrame#timerCard {
                background-color: #1B1624;
                border: 1px solid #3A2D48;
                border-radius: 18px;
            }

            QFrame#taskPanel {
                background-color: #15111C;
                border: 1px solid #352A42;
                border-radius: 10px;
            }

            QLabel#eyebrow {
                color: #A58AF5;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QLabel#timerTitle {
                color: #F2EAF9;
                font-size: 23px;
                font-weight: bold;
            }

            QLabel#timerSubtitle {
                color: #A69AAF;
                font-size: 12px;
            }

            QLabel#taskHeading {
                color: #A69AAF;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#taskInfo {
                color: #BDAED0;
                font-size: 12px;
            }

            QLabel#modeLabel {
                color: #D6C8F4;
                background-color: #30263B;
                border: 1px solid #493957;
                border-radius: 10px;
                padding: 7px 18px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#timerDisplay {
                color: #E9C5DF;
                font-weight: bold;
            }

            QLabel#timeHint {
                color: #A69AAF;
                font-size: 10px;
                letter-spacing: 1px;
            }

            QLabel#sessionLabel {
                color: #C7B5D6;
                font-size: 12px;
            }

            QLabel#messageLabel {
                color: #A69AAF;
                font-size: 12px;
            }

            QComboBox {
                background-color: #211A2D;
                color: #F2EAF9;
                border: 1px solid #493957;
                border-radius: 8px;
                padding: 9px 11px;
                min-height: 20px;
            }

            QComboBox:hover {
                border-color: #A58AF5;
            }

            QComboBox:focus {
                border: 1px solid #A58AF5;
            }

            QComboBox:disabled {
                color: #887D98;
                background-color: #191421;
            }

            QComboBox::drop-down {
                border: none;
                width: 24px;
            }

            QComboBox QAbstractItemView {
                background-color: #211A2D;
                color: #F2EAF9;
                border: 1px solid #493957;
                selection-background-color: #48345F;
                selection-color: white;
                padding: 5px;
            }

            QPushButton {
                background-color: #292236;
                color: #E9DDF5;
                border: 1px solid #443653;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #392E4B;
                border-color: #A58AF5;
            }

            QPushButton:pressed {
                background-color: #48345F;
            }

            QPushButton:disabled {
                background-color: #211A2D;
                color: #766B83;
                border-color: #30263B;
            }

            QPushButton#startButton {
                background-color: #A58AF5;
                color: #160F20;
                border: none;
                font-weight: bold;
            }

            QPushButton#startButton:hover {
                background-color: #BBA8FA;
            }

            QPushButton#resetButton {
                background-color: #30263B;
                color: #E9C5DF;
                border: 1px solid #57405D;
            }

            QPushButton#resetButton:hover {
                background-color: #44304A;
                border-color: #E9C5DF;
            }

            QPushButton#refreshTasksButton {
                background-color: #30263B;
                color: #D6C8F4;
                border: 1px solid #493957;
            }

            QProgressBar {
                background-color: #30263B;
                border: none;
                border-radius: 4px;
                height: 9px;
            }

            QProgressBar::chunk {
                background-color: #A58AF5;
                border-radius: 4px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(0)

        # Timer card
        card = QFrame()
        card.setObjectName("timerCard")
        card.setMaximumWidth(720)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        self.card_layout = QVBoxLayout(card)
        self.card_layout.setContentsMargins(
            26, 20, 26, 22
        )
        self.card_layout.setSpacing(10)

        # Header
        eyebrow = QLabel("TASKFORGE / FOCUS WORKSPACE")
        eyebrow.setObjectName("eyebrow")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(eyebrow)

        title = QLabel("Focus Timer")
        title.setObjectName("timerTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(title)

        subtitle = QLabel(
            "Stay focused. Make every session count."
        )
        subtitle.setObjectName("timerSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(subtitle)

        # Task selection panel
        task_panel = QFrame()
        task_panel.setObjectName("taskPanel")

        self.task_panel_layout = QVBoxLayout(task_panel)
        self.task_panel_layout.setContentsMargins(
            13, 10, 13, 10
        )
        self.task_panel_layout.setSpacing(7)

        task_heading = QLabel("CURRENT TASK")
        task_heading.setObjectName("taskHeading")

        self.task_panel_layout.addWidget(task_heading)

        task_row = QHBoxLayout()
        task_row.setSpacing(8)

        self.task_selector = QComboBox()
        self.task_selector.setMinimumWidth(0)
        self.task_selector.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.task_selector.currentIndexChanged.connect(
            self.on_task_changed
        )

        self.refresh_tasks_button = QPushButton("Refresh")
        self.refresh_tasks_button.setObjectName(
            "refreshTasksButton"
        )

        self.refresh_tasks_button.clicked.connect(
            self.refresh_tasks
        )

        task_row.addWidget(self.task_selector, 1)
        task_row.addWidget(self.refresh_tasks_button)

        self.task_panel_layout.addLayout(task_row)

        self.task_info = QLabel(
            "Select a task before starting."
        )
        self.task_info.setObjectName("taskInfo")
        self.task_info.setWordWrap(True)

        self.task_panel_layout.addWidget(self.task_info)

        self.card_layout.addWidget(task_panel)

        # Timer mode
        self.mode_label = QLabel()
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(
            self.mode_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Digital timer
        self.time_hint = QLabel("TIME REMAINING")
        self.time_hint.setObjectName("timeHint")
        self.time_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(self.time_hint)

        self.timer_display = QLabel("25:00")
        self.timer_display.setObjectName("timerDisplay")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(self.timer_display)

        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, self.WORK_SECONDS)
        self.progress_bar.setValue(0)

        self.card_layout.addWidget(self.progress_bar)

        # Completed sessions
        self.session_label = QLabel()
        self.session_label.setObjectName("sessionLabel")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(self.session_label)

        # Status message
        self.message_label = QLabel(
            "Select a task and start focusing."
        )
        self.message_label.setObjectName("messageLabel")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)

        self.card_layout.addWidget(self.message_label)

        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.start_button = QPushButton("Start Focus")
        self.start_button.setObjectName("startButton")
        self.start_button.setMinimumWidth(130)

        self.start_button.clicked.connect(
            self.toggle_timer
        )

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setMinimumWidth(100)

        self.reset_button.clicked.connect(
            self.reset_timer
        )

        self.stop_cycle_button = QPushButton("Stop Cycle")
        self.stop_cycle_button.setObjectName("resetButton")
        self.stop_cycle_button.setMinimumWidth(105)
        self.stop_cycle_button.clicked.connect(self.stop_cycle)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.stop_cycle_button)

        self.card_layout.addLayout(buttons_layout)

        # Center the card horizontally.
        # It grows with the window but never exceeds 720 px.
        card_row = QHBoxLayout()
        card_row.setContentsMargins(0, 0, 0, 0)
        card_row.addStretch(1)
        card_row.addWidget(card, 4)
        card_row.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(card_row)
        main_layout.addStretch(1)

        self._apply_responsive_layout()

    # =====================================
    # RESPONSIVE LAYOUT
    # =====================================

    def _apply_responsive_layout(self):

        if not hasattr(self, "timer_display"):
            return

        compact = (
            self.width() < 850
            or self.height() < 540
        )

        if compact:
            self.card_layout.setContentsMargins(
                18, 12, 18, 14
            )
            self.card_layout.setSpacing(7)

            self.task_panel_layout.setContentsMargins(
                11, 8, 11, 8
            )
            self.task_panel_layout.setSpacing(5)

            font_size = 43

        else:
            self.card_layout.setContentsMargins(
                26, 20, 26, 22
            )
            self.card_layout.setSpacing(10)

            self.task_panel_layout.setContentsMargins(
                13, 10, 13, 10
            )
            self.task_panel_layout.setSpacing(7)

            font_size = 56

        self.timer_display.setFont(
            QFont(
                "Segoe UI",
                font_size,
                QFont.Weight.Bold
            )
        )

    def resizeEvent(self, event):

        super().resizeEvent(event)
        self._apply_responsive_layout()

    # =====================================
    # TASK SELECTION
    # =====================================

    def refresh_tasks(self):

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

                if status == "completed":
                    continue

                self.task_selector.addItem(
                    title,
                    task_id
                )

            index = self.task_selector.findData(current_id)

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

        if self.mode == "work":

            if self.selected_task_id is None:
                self.message_label.setText(
                    "Please select a task first."
                )
                return

            if self.session_started_at is None:
                self.session_task_id = self.selected_task_id
                self.session_task_title = (
                    self.task_selector.currentText()
                )

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

        # During a break, allow choosing the task for the next focus session.
        controls_enabled = self.mode != "work"
        self.task_selector.setEnabled(controls_enabled)
        self.refresh_tasks_button.setEnabled(controls_enabled)

        if self.mode == "work":
            self.message_label.setText(
                "Stay focused. Keep going!"
            )
        else:
            self.message_label.setText(
                "Enjoy your break. Recharge!"
            )

        self.update_display()

    def pause_timer(self):

        self.timer.stop()
        self.is_running = False

        self.message_label.setText(
            "Timer paused."
        )

        self.update_display()

    def reset_timer(self):

        self.timer.stop()
        self.is_running = False

        if self.mode == "work":
            self.clear_active_session()

        self.remaining_seconds = self.get_current_duration()

        self.task_selector.setEnabled(True)
        self.refresh_tasks_button.setEnabled(True)

        self.message_label.setText(
            "Timer reset."
        )

        self.update_display()

    def stop_cycle(self):
        """Stop automatic phase switching and return to a fresh focus timer."""
        self.timer.stop()
        self.is_running = False

        # An unfinished focus session is deliberately not written to history.
        self.clear_active_session()

        self.mode = "work"
        self.remaining_seconds = self.WORK_SECONDS

        self.task_selector.setEnabled(True)
        self.refresh_tasks_button.setEnabled(True)

        self.message_label.setText(
            "Pomodoro cycle stopped. Ready when you are."
        )

        self.update_display()

    def _on_tick(self):

        self.remaining_seconds -= 1

        if (
            self.mode == "work"
            and self.session_started_at is not None
        ):
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

        # Re-enable task controls between phases. start_timer() will lock
        # them again during focus and keep them available during breaks.
        self.task_selector.setEnabled(True)
        self.refresh_tasks_button.setEnabled(True)

        if self.mode == "work":

            session_saved = self.save_completed_session()
            self.completed_work_sessions += 1

            if (
                self.completed_work_sessions
                % self.SESSIONS_BEFORE_LONG_BREAK == 0
            ):
                self.mode = "long_break"
            else:
                self.mode = "short_break"

            if session_saved:
                self.message_label.setText(
                    "Session saved! Enjoy your break."
                )
            else:
                self.message_label.setText(
                    "Focus session completed. Enjoy your break."
                )

        else:

            self.mode = "work"

            self.message_label.setText(
                "Break completed. Starting your next focus session."
            )

        self.remaining_seconds = self.get_current_duration()

        # Keep the selected task. This lets the next focus session start
        # automatically after the break without asking for the task again.
        self.update_display()
        self.start_timer()

    def update_display(self):

        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60

        self.timer_display.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        if self.mode == "work":
            self.mode_label.setText("FOCUS SESSION")
            phase_name = "Focus"
        elif self.mode == "short_break":
            self.mode_label.setText("SHORT BREAK")
            phase_name = "Break"
        else:
            self.mode_label.setText("LONG BREAK")
            phase_name = "Break"

        total_duration = self.get_current_duration()

        self.progress_bar.setRange(
            0,
            total_duration
        )

        self.progress_bar.setValue(
            total_duration - self.remaining_seconds
        )

        self.session_label.setText(
            f"Completed focus sessions: "
            f"{self.completed_work_sessions}"
        )

        # Keep the button label synchronized with the timer's current state.
        if self.is_running:
            self.start_button.setText(f"Pause {phase_name}")
        elif self.remaining_seconds < total_duration:
            self.start_button.setText(f"Resume {phase_name}")
        else:
            self.start_button.setText(f"Start {phase_name}")
