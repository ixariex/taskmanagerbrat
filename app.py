import sys

from PyQt6.QtWidgets import QApplication
from database.database import create_db
from ui.main_window import MainWindow
from ui.text_interaction import install_text_interaction


def main():
    create_db()

    app = QApplication(sys.argv)

    install_text_interaction(app)

    window = MainWindow()
    window.show()


    sys.exit(app.exec())


if __name__ == "__main__":
    main()