from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.settings_manager import DEFAULT_SETTINGS
from core.theme_manager import ACCENT_PRESETS, THEME_PRESETS


CUSTOM_COLOR_SLOTS = [
    ("window_bg", "Background"),
    ("card_bg", "Cards"),
    ("text_primary", "Main text"),
    ("text_secondary", "Secondary text"),
]


# noinspection PyArgumentList
class SettingsWidget(QWidget):
    # noinspection PyArgumentList
    settingsChanged = pyqtSignal(dict)
    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self._accent_color = DEFAULT_SETTINGS["accent_color"]
        self._last_accent_index = 0
        self._custom_colors: dict[str, str] = dict(THEME_PRESETS["dark"])
        self._slot_buttons: dict[str, QPushButton] = {}

        self.setStyleSheet("""
            QWidget#settingsPage { background: transparent; color: #F2EAF9; }
            QLabel#settingsEyebrow {
                color: #A58AF5; font-size: 10px; font-weight: bold;
                letter-spacing: 2px;
            }
            QLabel#settingsTitle { color: #F2EAF9; font-size: 27px; font-weight: bold; }
            QLabel#settingsSubtitle { color: #A69AAF; font-size: 12px; }
            QFrame#settingsCard {
                background-color: #1B1624; border: 1px solid #33283F;
                border-radius: 14px;
            }
            QLabel#settingName { color: #E9C5DF; font-size: 15px; font-weight: bold; }
            QLabel#settingDescription { color: #A69AAF; font-size: 11px; }
            QPushButton#resetSettingsButton {
                background-color: #292236; color: #D6C8F4;
                border: 1px solid #443653; border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton#resetSettingsButton:hover { background-color: #392E4B; }
            QPushButton#customColorButton {
                background-color: #30263B; color: #F2EAF9;
                border: 1px solid #493957; border-radius: 8px;
                padding: 9px 13px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(15)

        header = QVBoxLayout()
        header.setSpacing(4)
        eyebrow = QLabel("TASKFORGE / PREFERENCES")
        eyebrow.setObjectName("settingsEyebrow")
        title = QLabel("Settings")
        title.setObjectName("settingsTitle")
        subtitle = QLabel("Personalize the look and feel of your workspace.")
        subtitle.setObjectName("settingsSubtitle")
        header.addWidget(eyebrow)
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        card = QFrame()
        card.setObjectName("settingsCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(18)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        self.theme_combo.addItem("System", "system")
        self.theme_combo.addItem("Custom", "custom")
        card_layout.addLayout(self._make_setting_row(
            "Theme",
            "Choose a dark, light, system-based, or custom appearance.",
            self.theme_combo,
        ))

        self.custom_palette_row = QWidget()
        palette_layout = QHBoxLayout(self.custom_palette_row)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setSpacing(10)

        palette_info = QVBoxLayout()
        palette_info.setSpacing(4)
        p_name = QLabel("Custom palette")
        p_name.setObjectName("settingName")
        p_desc = QLabel("Pick your own background, card, and text colors.")
        p_desc.setObjectName("settingDescription")
        palette_info.addWidget(p_name)
        palette_info.addWidget(p_desc)
        palette_layout.addLayout(palette_info, 1)

        for key, label in CUSTOM_COLOR_SLOTS:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key, lbl=label: self._pick_slot_color(k, lbl))
            self._slot_buttons[key] = btn
            palette_layout.addWidget(btn)

        card_layout.addWidget(self.custom_palette_row)

        accent_controls = QHBoxLayout()
        accent_controls.setSpacing(8)
        self.accent_combo = QComboBox()
        for name, color in ACCENT_PRESETS.items():
            self.accent_combo.addItem(name, color)
        self.accent_combo.addItem("Custom color…", "custom")
        accent_controls.addWidget(self.accent_combo, 1)

        self.custom_color_button = QPushButton("Choose color")
        self.custom_color_button.setObjectName("customColorButton")
        self.custom_color_button.clicked.connect(self.choose_custom_color)
        accent_controls.addWidget(self.custom_color_button)
        card_layout.addLayout(self._make_setting_row(
            "Accent color",
            "Change highlights, active navigation, and primary controls.",
            accent_controls,
        ))

        self.scale_combo = QComboBox()
        self.scale_combo.addItem("Small", "small")
        self.scale_combo.addItem("Medium", "medium")
        self.scale_combo.addItem("Large", "large")
        card_layout.addLayout(self._make_setting_row(
            "Text size",
            "Adjust text throughout the application.",
            self.scale_combo,
        ))

        root.addWidget(card)
        root.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()
        self.reset_button = QPushButton("Restore defaults")
        self.reset_button.setObjectName("resetSettingsButton")
        self.reset_button.clicked.connect(self.restore_defaults)
        footer.addWidget(self.reset_button)
        root.addLayout(footer)

        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.accent_combo.currentIndexChanged.connect(self._accent_selection_changed)
        self.scale_combo.currentIndexChanged.connect(self._emit_settings)

        self.set_settings(settings or DEFAULT_SETTINGS)

    @staticmethod
    def _make_setting_row(title, description, control):
        row = QHBoxLayout()
        row.setSpacing(20)
        text_column = QVBoxLayout()
        text_column.setSpacing(4)
        name_label = QLabel(title)
        name_label.setObjectName("settingName")
        description_label = QLabel(description)
        description_label.setObjectName("settingDescription")
        description_label.setWordWrap(True)
        text_column.addWidget(name_label)
        text_column.addWidget(description_label)
        row.addLayout(text_column, 1)
        if isinstance(control, QComboBox):
            row.addWidget(control, 0)
        else:
            row.addLayout(control, 0)
        return row

    def _style_slot_button(self, key: str, label: str) -> None:
        hex_color = self._custom_colors.get(key, THEME_PRESETS["dark"][key])
        text_color = "#18181B" if QColor(hex_color).lightness() > 130 else "#FFFFFF"
        btn = self._slot_buttons[key]
        btn.setText(f"{label}: {hex_color}")
        qss = (
            f"background-color: {hex_color}; color: {text_color}; "
            "border: 1px solid #493957; border-radius: 8px; "
            "padding: 8px 11px; font-weight: bold; font-size: 11px;"
        )
        btn.setProperty("_taskforge_skip_theme", True)
        btn.setStyleSheet(qss)


    def _refresh_slot_buttons(self) -> None:
        for key, label in CUSTOM_COLOR_SLOTS:
            self._style_slot_button(key, label)

    def _pick_slot_color(self, key: str, label: str) -> None:
        current = QColor(self._custom_colors.get(key, THEME_PRESETS["dark"][key]))
        color = QColorDialog.getColor(current, self, f"Choose {label.lower()} color")
        if not color.isValid():
            return

        hex_val = color.name().upper()
        self._custom_colors[key] = hex_val

        c = QColor(hex_val)
        is_light = c.lightness() > 128
        if key == "window_bg":
            self._custom_colors["sidebar_bg"] = (c.darker(104) if is_light else c.lighter(115)).name().upper()
            self._custom_colors["page_bg"] = (c.darker(102) if is_light else c.lighter(125)).name().upper()
        elif key == "card_bg":
            self._custom_colors["card_alt_bg"] = (c.darker(105) if is_light else c.lighter(118)).name().upper()
            self._custom_colors["control_bg"] = (c.darker(109) if is_light else c.lighter(132)).name().upper()
            self._custom_colors["control_hover"] = (c.darker(114) if is_light else c.lighter(148)).name().upper()
            self._custom_colors["border_subtle"] = (c.darker(112) if is_light else c.lighter(155)).name().upper()
            self._custom_colors["border_default"] = (c.darker(120) if is_light else c.lighter(175)).name().upper()
        elif key == "text_primary":
            self._custom_colors["text_secondary"] = (c.lighter(135) if not is_light else c.darker(120)).name().upper()
            self._custom_colors["text_muted"] = (c.darker(145) if not is_light else c.lighter(165)).name().upper()
        elif key == "text_secondary":
            self._custom_colors["text_muted"] = hex_val

        self._style_slot_button(key, label)
        self._emit_settings()

    def set_settings(self, settings):
        settings = dict(DEFAULT_SETTINGS, **(settings or {}))
        self.theme_combo.blockSignals(True)
        self.accent_combo.blockSignals(True)
        self.scale_combo.blockSignals(True)

        theme = settings.get("theme", "dark")
        theme_index = self.theme_combo.findData(theme)
        self.theme_combo.setCurrentIndex(max(0, theme_index))

        self._accent_color = QColor(settings.get("accent_color", DEFAULT_SETTINGS["accent_color"])).name().upper()
        accent_index = self.accent_combo.findData(self._accent_color)
        if accent_index < 0:
            custom_index = self.accent_combo.findData("custom")
            self.accent_combo.setCurrentIndex(custom_index)
        else:
            self.accent_combo.setCurrentIndex(accent_index)
        self._last_accent_index = self.accent_combo.currentIndex()

        scale_index = self.scale_combo.findData(settings.get("text_scale", "medium"))
        self.scale_combo.setCurrentIndex(max(0, scale_index))

        saved_custom = settings.get("custom_colors") or {}
        self._custom_colors = {**THEME_PRESETS["dark"], **saved_custom}
        self._refresh_slot_buttons()
        self.custom_palette_row.setVisible(theme == "custom")

        self.theme_combo.blockSignals(False)
        self.accent_combo.blockSignals(False)
        self.scale_combo.blockSignals(False)
        self._update_custom_color_button()

    def current_settings(self):
        return {
            "theme": self.theme_combo.currentData(),
            "accent_color": self._accent_color,
            "text_scale": self.scale_combo.currentData(),
            "custom_colors": dict(self._custom_colors),
        }

    def _on_theme_changed(self, *_args):
        self.custom_palette_row.setVisible(self.theme_combo.currentData() == "custom")
        self._emit_settings()

    def _emit_settings(self, *_args):
        self.settingsChanged.emit(self.current_settings())

    def _accent_selection_changed(self, index):
        selected = self.accent_combo.itemData(index)
        if selected == "custom":
            self.choose_custom_color()
            return
        if selected:
            self._accent_color = QColor(selected).name().upper()
            self._last_accent_index = index
            self._update_custom_color_button()
            self._emit_settings()

    def choose_custom_color(self):
        color = QColorDialog.getColor(QColor(self._accent_color), self, "Choose accent color")
        if not color.isValid():
            self.accent_combo.blockSignals(True)
            self.accent_combo.setCurrentIndex(self._last_accent_index)
            self.accent_combo.blockSignals(False)
            return

        self._accent_color = color.name().upper()
        custom_index = self.accent_combo.findData("custom")
        self.accent_combo.blockSignals(True)
        self.accent_combo.setCurrentIndex(custom_index)
        self.accent_combo.blockSignals(False)
        self._last_accent_index = custom_index
        self._update_custom_color_button()
        self._emit_settings()

    def _update_custom_color_button(self):
        text_color = "#18181B" if QColor(self._accent_color).lightness() > 140 else "#FFFFFF"
        self.custom_color_button.setProperty("_taskforge_skip_theme", True)
        self.custom_color_button.setStyleSheet(
            "QPushButton#customColorButton {"
            f"background-color: {self._accent_color};"
            f"color: {text_color}; border: 1px solid #493957;"
            "border-radius: 8px; padding: 9px 13px; font-weight: bold; }"
        )


    def restore_defaults(self):
        self.set_settings(DEFAULT_SETTINGS)
        self._emit_settings()
