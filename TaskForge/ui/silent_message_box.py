
from PyQt6.QtWidgets import QMessageBox as QtMessageBox

from ui.dialog_theme import DIALOG_STYLESHEET


class SilentMessageBox:
    StandardButton = QtMessageBox.StandardButton

    @staticmethod
    def _show(
        parent,
        title,
        text,
        buttons,
        default_button
    ):
        message_box = QtMessageBox(parent)

        # No system icon = no standard Windows notification sound.
        message_box.setIcon(QtMessageBox.Icon.NoIcon)

        message_box.setWindowTitle(title)
        message_box.setText(str(text))
        message_box.setStandardButtons(buttons)
        message_box.setStyleSheet(DIALOG_STYLESHEET)

        if default_button != QtMessageBox.StandardButton.NoButton:
            message_box.setDefaultButton(default_button)

        return QtMessageBox.StandardButton(message_box.exec())

    @staticmethod
    def information(
        parent,
        title,
        text,
        buttons=QtMessageBox.StandardButton.Ok,
        default_button=QtMessageBox.StandardButton.NoButton
    ):
        return SilentMessageBox._show(
            parent, title, text, buttons, default_button
        )

    @staticmethod
    def warning(
        parent,
        title,
        text,
        buttons=QtMessageBox.StandardButton.Ok,
        default_button=QtMessageBox.StandardButton.NoButton
    ):
        return SilentMessageBox._show(
            parent, title, text, buttons, default_button
        )

    @staticmethod
    def critical(
        parent,
        title,
        text,
        buttons=QtMessageBox.StandardButton.Ok,
        default_button=QtMessageBox.StandardButton.NoButton
    ):
        return SilentMessageBox._show(
            parent, title, text, buttons, default_button
        )

    @staticmethod
    def question(
        parent,
        title,
        text,
        buttons=(
            QtMessageBox.StandardButton.Yes
            | QtMessageBox.StandardButton.No
        ),
        default_button=QtMessageBox.StandardButton.NoButton
    ):
        return SilentMessageBox._show(
            parent, title, text, buttons, default_button
        )
