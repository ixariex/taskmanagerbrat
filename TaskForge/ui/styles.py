from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


APP_STYLESHEET = """
QWidget#appRoot {
    background-color: #100D16;
    color: #F2EAF9;
    font-family: "Segoe UI";
    font-size: 14px;
}

QWidget#sidebar {
    background-color: #0B0910;
    border-right: 1px solid #292234;
}

QLabel#brand {
    color: #D6C8F4;
    font-size: 27px;
    font-weight: bold;
}

QLabel#sidebarSubtitle {
    color: #93879F;
    font-size: 11px;
    letter-spacing: 1px;
}

QPushButton {
    background-color: #211A2D;
    color: #EDE5F8;
    border: 1px solid #382E46;
    border-radius: 8px;
    padding: 9px 14px;
}

QPushButton:hover {
    background-color: #30243E;
    border-color: #9577DB;
}

QPushButton:pressed {
    background-color: #413154;
}

QPushButton#navButton {
    background-color: transparent;
    color: #B9ADCA;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding: 13px;
    font-size: 14px;
}

QPushButton#navButton:hover {
    background-color: #211A2D;
    color: #F2EAF9;
}

QPushButton#navButton:checked {
    background-color: #342644;
    color: #D6C2FF;
    font-weight: bold;
    border-left: 3px solid #A58AF5;
}

QLabel#pageTitle {
    font-size: 28px;
    font-weight: bold;
    color: #F2EAF9;
}

QLabel#pageSubtitle {
    color: #A69AAF;
    font-size: 13px;
}

QFrame#statCard {
    background-color: #1B1624;
    border: 1px solid #33283F;
    border-radius: 14px;
}

QLabel#statTitle {
    color: #B8A9C9;
    font-size: 13px;
}

QLabel#statValue {
    color: #D6C8F4;
    font-size: 30px;
    font-weight: bold;
}

QListWidget {
    background-color: #191421;
    color: #F0E9F7;
    border: 1px solid #352A42;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    background-color: transparent;
    padding: 13px;
    border-bottom: 1px solid #30273A;
    border-radius: 6px;
}

QListWidget::item:hover {
    background-color: #282034;
}

QListWidget::item:selected {
    background-color: #392B4D;
    color: #E5D6FF;
}

QLineEdit,
QComboBox,
QTextEdit,
QDateEdit,
QSpinBox,
QTimeEdit {
    background-color: #1C1725;
    color: #F2EAF9;
    border: 1px solid #3A3048;
    border-radius: 8px;
    padding: 9px;
    selection-background-color: #8062C8;
}

QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus,
QDateEdit:focus,
QSpinBox:focus {
    border: 1px solid #A58AF5;
}

QComboBox::drop-down {
    border: none;
    width: 25px;
}

QComboBox QAbstractItemView {
    background-color: #211A2D;
    color: #F2EAF9;
    selection-background-color: #48345F;
    border: 1px solid #453654;
}

QPushButton#primaryButton {
    background-color: #8D6BD0;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #A58AF5;
    color: #150F20;
}

QPushButton#secondaryButton {
    background-color: #292236;
    color: #D6C8F4;
    border: 1px solid #443653;
    border-radius: 8px;
    padding: 10px 18px;
}

QPushButton#secondaryButton:hover {
    background-color: #392E4B;
}

QPushButton#dangerButton {
    background-color: #38202F;
    color: #F2C5DF;
    border: 1px solid #684052;
    border-radius: 8px;
    padding: 10px 18px;
}

QPushButton#dangerButton:hover {
    background-color: #553047;
    border-color: #E9AFCF;
}

QScrollBar:vertical {
    background-color: #15111C;
    width: 9px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #58446D;
    border-radius: 4px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A58AF5;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QToolTip {
    background-color: #292136;
    color: #F2EAF9;
    border: 1px solid #8D6BD0;
    padding: 5px;
}
"""


PAGE_COMMON_STYLESHEET = """
QLabel#pageEyebrow {
    color: #A58AF5;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    background: transparent;
}

QLabel#heroTitle {
    color: #F2EAF9;
    font-size: 27px;
    font-weight: bold;
    background: transparent;
}

QLabel#heroSubtitle {
    color: #A69AAF;
    font-size: 12px;
    background: transparent;
}

QLabel#sectionTitle {
    color: #E9C5DF;
    font-size: 17px;
    font-weight: bold;
    background: transparent;
}

QLabel#countBadge {
    color: #D6C8F4;
    background-color: #30263B;
    border: 1px solid #493957;
    border-radius: 9px;
    padding: 7px 12px;
    font-weight: bold;
}

QFrame#contentPanel {
    background-color: #1B1624;
    border: 1px solid #352A42;
    border-radius: 14px;
}

QListWidget#cardList {
    background-color: #15111C;
    color: #F2EAF9;
    border: 1px solid #352A42;
    border-radius: 10px;
    padding: 8px;
    outline: none;
}

QListWidget#cardList::item {
    background-color: #1D1727;
    color: #F2EAF9;
    padding: 13px;
    margin: 3px 1px;
    border: 1px solid #30263B;
    border-radius: 8px;
}

QListWidget#cardList::item:hover {
    background-color: #292136;
    border-color: #57446D;
}

QListWidget#cardList::item:selected {
    background-color: #392B4D;
    border-color: #A58AF5;
    color: #FFFFFF;
}
"""


def create_stat_card(title: str) -> tuple[QFrame, QLabel]:
    card = QFrame()
    card.setObjectName("statCard")
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(20, 18, 20, 18)
    card_layout.setSpacing(10)

    title_label = QLabel(title)
    title_label.setObjectName("statTitle")
    value_label = QLabel("0")
    value_label.setObjectName("statValue")

    card_layout.addWidget(title_label)
    card_layout.addWidget(value_label)
    return card, value_label
