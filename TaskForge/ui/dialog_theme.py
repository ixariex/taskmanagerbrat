
DIALOG_STYLESHEET = """
QDialog {
    background-color: #100D16;
    color: #F2EAF9;
    font-family: "Segoe UI";
    font-size: 13px;
}

QLabel {
    color: #D6C8E5;
    background: transparent;
    font-size: 13px;
}

QLineEdit,
QTextEdit,
QSpinBox,
QComboBox,
QDateEdit {
    background-color: #1B1624;
    color: #F2EAF9;
    border: 1px solid #40344F;
    border-radius: 8px;
    padding: 9px 11px;
    selection-background-color: #8062C8;
    selection-color: white;
}

QLineEdit:hover,
QTextEdit:hover,
QSpinBox:hover,
QComboBox:hover,
QDateEdit:hover {
    border-color: #8065A8;
}

QLineEdit:focus,
QTextEdit:focus,
QSpinBox:focus,
QComboBox:focus,
QDateEdit:focus {
    border: 1px solid #A58AF5;
}

QLineEdit:disabled,
QComboBox:disabled,
QDateEdit:disabled {
    background-color: #15111C;
    color: #766B83;
    border-color: #30263B;
}

QComboBox::drop-down,
QDateEdit::drop-down {
    border: none;
    width: 26px;
}

QComboBox QAbstractItemView {
    background-color: #211A2D;
    color: #F2EAF9;
    border: 1px solid #493957;
    selection-background-color: #48345F;
    selection-color: white;
    padding: 5px;
}

QCheckBox {
    color: #D6C8E5;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #57466B;
    border-radius: 4px;
    background-color: #1B1624;
}

QCheckBox::indicator:checked {
    background-color: #A58AF5;
    border-color: #A58AF5;
}

QPushButton {
    background-color: #292236;
    color: #E9DDF5;
    border: 1px solid #443653;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #392E4B;
    border-color: #A58AF5;
}

QPushButton:pressed {
    background-color: #48345F;
}

QPushButton#primaryButton {
    background-color: #A58AF5;
    color: #160F20;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #BBA8FA;
}

QPushButton#cancelButton {
    background-color: #30263B;
    color: #E9C5DF;
    border: 1px solid #57405D;
}

QDialogButtonBox QPushButton {
    min-width: 85px;
    min-height: 18px;
}

QCalendarWidget QWidget {
    background-color: #1B1624;
    color: #F2EAF9;
}

QCalendarWidget QToolButton {
    background-color: #292236;
    color: #D6C8F4;
    border: none;
    border-radius: 5px;
    padding: 5px;
}

QCalendarWidget QToolButton:hover {
    background-color: #493957;
}

QCalendarWidget QAbstractItemView {
    background-color: #1B1624;
    color: #F2EAF9;
    selection-background-color: #8062C8;
    selection-color: white;
}

QMessageBox {
    background-color: #100D16;
    color: #F2EAF9;
}

QMessageBox QLabel {
    color: #F2EAF9;
    min-width: 220px;
}

QMessageBox QPushButton {
    min-width: 75px;
}

QToolTip {
    background-color: #292136;
    color: #F2EAF9;
    border: 1px solid #8D6BD0;
    padding: 5px;
}

QScrollBar:vertical {
    background-color: #15111C;
    width: 8px;
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
"""
