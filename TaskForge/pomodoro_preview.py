import sys

from PyQt6.QtWidgets import QApplication
from ui.pomodoro_widget import PomodoroWidget


def main():
    app = QApplication(sys.argv)

    window = PomodoroWidget()
    window.setWindowTitle("TaskForge - Pomodoro")
    window.resize(750, 650)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()