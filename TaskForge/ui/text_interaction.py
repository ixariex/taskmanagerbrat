
"""
TaskForge Global Text Interaction Manager.

Provides text selection, copying and context menus
throughout the entire application.
"""

from PyQt6.QtCore import QObject, QEvent, Qt
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QAbstractItemView,
    QComboBox,
    QMenu,
)


class TextInteractionFilter(QObject):

    def eventFilter(self, watched, event):

        # Enable text selection on every QLabel.
        if (
            event.type() == QEvent.Type.Show
            and isinstance(watched, QLabel)
        ):
            flags = watched.textInteractionFlags()

            flags |= Qt.TextInteractionFlag.TextSelectableByMouse
            flags &= ~Qt.TextInteractionFlag.TextSelectableByKeyboard

            watched.setTextInteractionFlags(flags)
            watched.setCursor(Qt.CursorShape.IBeamCursor)

        # Handle Ctrl+C and Ctrl+A globally.
        if event.type() == QEvent.Type.KeyPress:

            modifiers = event.modifiers()
            key = event.key()

            if modifiers & Qt.KeyboardModifier.ControlModifier:

                # Copy text from labels, lists and combo boxes.
                if key == Qt.Key.Key_C:

                    text = self._get_copy_text(watched)

                    if text is not None:
                        QApplication.clipboard().setText(text)
                        event.accept()
                        return True

                # Select all text or list items.
                elif key == Qt.Key.Key_A:

                    if isinstance(watched, QLabel):
                        watched.setSelection(
                            0,
                            len(watched.text())
                        )
                        event.accept()
                        return True

                    if isinstance(watched, QAbstractItemView):
                        watched.selectAll()
                        event.accept()
                        return True

        # Handle right-click context menus.
        if event.type() == QEvent.Type.ContextMenu:

            if isinstance(
                watched,
                (QLabel, QListWidget, QAbstractItemView, QComboBox)
            ):
                self._show_context_menu(watched, event)
                return True

        return super().eventFilter(watched, event)

    @staticmethod
    def _get_copy_text(widget):

        # QLabel
        if isinstance(widget, QLabel):

            if widget.hasSelectedText():
                return widget.selectedText()

            text = widget.text()

            if widget.textFormat() == Qt.TextFormat.RichText:
                document = QTextDocument()
                document.setHtml(text)
                text = document.toPlainText()

            return text if text else None

        # QListWidget
        if isinstance(widget, QListWidget):

            selected_items = widget.selectedItems()

            if not selected_items and widget.currentItem():
                selected_items = [widget.currentItem()]

            if selected_items:
                return "\n".join(
                    item.text() for item in selected_items
                )

        # Other item views, including tables.
        elif isinstance(widget, QAbstractItemView):

            indexes = widget.selectedIndexes()

            if not indexes and widget.currentIndex().isValid():
                indexes = [widget.currentIndex()]

            if indexes:
                indexes = sorted(
                    indexes,
                    key=lambda index: (
                        index.row(),
                        index.column()
                    )
                )

                rows = {}

                for index in indexes:
                    rows.setdefault(index.row(), []).append(
                        str(index.data() or "")
                    )

                return "\n".join(
                    "\t".join(values)
                    for values in rows.values()
                )

        # QComboBox
        elif isinstance(widget, QComboBox):
            return widget.currentText()

        return None

    def _show_context_menu(self, widget, event):

        # Select the item under the cursor in lists.
        if isinstance(widget, QListWidget):
            item = widget.itemAt(event.pos())

            if item is not None and not item.isSelected():
                widget.setCurrentItem(item)

        elif isinstance(widget, QAbstractItemView):
            index = widget.indexAt(event.pos())

            if index.isValid():
                widget.setCurrentIndex(index)

        menu = QMenu(widget)

        copy_action = menu.addAction("Copy")

        select_all_action = None

        if isinstance(widget, (QLabel, QAbstractItemView)):
            select_all_action = menu.addAction("Select All")

        selected_action = menu.exec(event.globalPos())

        if selected_action == copy_action:

            text = self._get_copy_text(widget)

            if text is not None:
                QApplication.clipboard().setText(text)

        elif selected_action == select_all_action:

            if isinstance(widget, QLabel):
                widget.setSelection(
                    0,
                    len(widget.text())
                )

            elif isinstance(widget, QAbstractItemView):
                widget.selectAll()


def install_text_interaction(app):
    """
    Install global text interaction for the entire TaskForge app.
    """

    interaction_filter = TextInteractionFilter(app)

    app.installEventFilter(interaction_filter)

    # Keep a Python reference to the filter.
    app._taskforge_text_interaction_filter = interaction_filter

    return interaction_filter
