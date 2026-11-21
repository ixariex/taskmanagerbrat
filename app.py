
import sys

from PyQt6.QtWidgets import QApplication

from database.database import create_db
from ui.main_window import MainWindow


def main() -> int:
    create_db()
    app = QApplication(sys.argv)
    app.setApplicationName("TaskForge")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
