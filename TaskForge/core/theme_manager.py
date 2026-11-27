import re
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication
from core.settings_manager import TEXT_SCALE_FACTORS, normalize_settings


ACCENT_PRESETS = {
    "Purple": "#A58AF5",
    "Blue": "#62A8F7",
    "Green": "#55C79A",
    "Pink": "#E58BB8",
    "Orange": "#E6A15D",
}

# Человекочитаемые названия слотов для экрана настроек (чтобы юзер мог крутить их сам)
THEME_TOKEN_LABELS = {
    "window_bg": "Фон окна",
    "sidebar_bg": "Боковое меню",
    "page_bg": "Фон страниц",
    "card_bg": "Карточки и поля",
    "card_alt_bg": "Вложенные блоки",
    "control_bg": "Кнопки и элементы",
    "control_hover": "Кнопки при наведении",
    "border_subtle": "Тонкие границы",
    "border_default": "Границы кнопок и полей",
    "text_primary": "Основной текст",
    "text_secondary": "Второстепенный текст",
    "text_muted": "Приглушённый текст",
}

# Встроенные пресеты тем в едином формате токенов
THEME_PRESETS: dict[str, dict[str, str]] = {
    "dark": {
        "window_bg": "#121214",
        "sidebar_bg": "#161618",
        "page_bg": "#19191C",
        "card_bg": "#1F1F23",
        "card_alt_bg": "#242429",
        "control_bg": "#2A2A30",
        "control_hover": "#323239",
        "border_subtle": "#35353C",
        "border_default": "#42424B",
        "text_primary": "#F5F5F8",
        "text_secondary": "#DCDCE2",
        "text_muted": "#94949E",
    },
    "light": {
        "window_bg": "#ECECEE",
        "sidebar_bg": "#F3F3F5",
        "page_bg": "#F6F6F8",
        "card_bg": "#FFFFFF",
        "card_alt_bg": "#F2F2F5",
        "control_bg": "#E6E6EB",
        "control_hover": "#DFDFE5",
        "border_subtle": "#E2E2E7",
        "border_default": "#D4D4DB",
        "text_primary": "#18181B",
        "text_secondary": "#2C2C34",
        "text_muted": "#6E6E78",
    },
}

# Привязка всех старых HEX-кодов приложения к 12 семантическим токенам
LEGACY_HEX_TO_TOKEN: dict[str, str] = {
    # Фон
    "#0B0910": "window_bg",
    "#100D16": "sidebar_bg",
    "#15111C": "page_bg",
    "#191421": "page_bg",
    "#150F20": "window_bg",
    "#160F20": "window_bg",
    # Карточки
    "#1B1624": "card_bg",
    "#1C1725": "card_bg",
    "#1D1727": "card_alt_bg",
    "#211A2D": "card_alt_bg",
    "#292236": "card_alt_bg",
    # Контролы и ховеры
    "#282034": "control_bg",
    "#292136": "control_bg",
    "#30263B": "control_bg",
    "#30273A": "control_bg",
    "#292234": "control_hover",
    "#30243E": "control_hover",
    "#33283F": "control_hover",
    "#342644": "control_hover",
    "#352A42": "control_hover",
    # Границы
    "#382C48": "border_subtle",
    "#382E46": "border_subtle",
    "#392B4D": "border_subtle",
    "#392E4B": "border_subtle",
    "#3A3048": "border_default",
    "#40344F": "border_default",
    "#413154": "border_default",
    "#443653": "border_default",
    "#453654": "border_default",
    "#493957": "border_default",
    "#48345F": "border_default",
    "#57446D": "border_default",
    "#58446D": "border_default",
    # 1. Главный текст (заголовки страниц, названия задач, основной контент)
    "#EDE5F8": "text_primary",
    "#F0E9F7": "text_primary",
    "#F2EAF9": "text_primary",

    # 2. Второстепенный текст (подзаголовки, описания настроек, даты, метки)
    "#E9C5DF": "text_secondary",
    "#E9DFF1": "text_secondary",
    "#D6C8F4": "text_secondary",
    "#E5D6FF": "text_secondary",
    "#867A94": "text_secondary",
    "#93879F": "text_secondary",
    "#A69AAF": "text_secondary",
    "#B8A9C9": "text_secondary",
    "#B9ADCA": "text_secondary",

}


def build_palette_map(tokens: dict[str, str]) -> dict[str, str]:
    """Собирает итоговую карту замены HEX-цветов из переданных токенов."""
    base = dict(THEME_PRESETS["dark"])
    base.update(tokens)

    color_map = {
        legacy_hex: base[token_name].upper()
        for legacy_hex, token_name in LEGACY_HEX_TO_TOKEN.items()
    }

    # Автоматическая подстройка цветов предупреждений/удаления под яркость фона
    is_light = QColor(base["window_bg"]).lightness() > 128
    if is_light:
        color_map.update({
            "#38202F": "#F9ECEF",
            "#553047": "#F2D8DE",
            "#684052": "#E5C0C9",
            "#F2C5DF": "#8A3A58",
            "#E9AFCF": "#A64B6D",
        })
    else:
        color_map.update({
            "#38202F": "#2C2225",
            "#553047": "#3D2B30",
            "#684052": "#4D363C",
            "#F2C5DF": "#E8C8D6",
            "#E9AFCF": "#E0B4C8",
        })


    return color_map


def _resolve_theme_tokens(theme: str, custom_colors: dict[str, str] | None = None) -> dict[str, str]:
    if theme == "custom":
        merged = dict(THEME_PRESETS["dark"])
        if custom_colors:
            merged.update(custom_colors)
        return merged

    if theme == "system":
        app = QApplication.instance()
        if app is not None and app.styleHints().colorScheme() == Qt.ColorScheme.Light:
            return dict(THEME_PRESETS["light"])
        return dict(THEME_PRESETS["dark"])

    return dict(THEME_PRESETS.get(theme, THEME_PRESETS["dark"]))


def transform_stylesheet(
    stylesheet: str,
    theme: str,
    accent_color: str,
    text_scale: str,
    custom_colors: dict[str, str] | None = None,
) -> str:
    """Transform an original widget stylesheet without changing its saved source."""
    if not stylesheet:
        return stylesheet

    normalized = normalize_settings({
        "theme": theme,
        "accent_color": accent_color,
        "text_scale": text_scale,
    })

    tokens = _resolve_theme_tokens(normalized["theme"], custom_colors)
    color_map = build_palette_map(tokens)

    accent = QColor(normalized["accent_color"])
    accent_dark = accent.darker(118).name().upper()
    accent_hover = accent.lighter(115).name().upper()
    accent_soft = accent.lighter(135).name().upper()

    color_map.update({
        "#A58AF5": accent.name().upper(),
        "#9577DB": accent.name().upper(),
        "#8D6BD0": accent_dark,
        "#8062C8": accent_dark,
        "#BBA8FA": accent_hover,
        "#D6C2FF": accent_soft,
    })

    def replace_color(match: re.Match[str]) -> str:
        hex_code = match.group(0)
        return color_map.get(hex_code.upper(), hex_code)

    result = re.sub(r"#[0-9A-Fa-f]{6}\b", replace_color, stylesheet)

    factor = TEXT_SCALE_FACTORS[normalized["text_scale"]]
    if factor != 1.0:
        def scale_font(match: re.Match[str]) -> str:
            value = float(match.group(2)) * factor
            return f"{match.group(1)}{value:.1f}px"

        result = re.sub(
            r"(font-size\s*:\s*)(\d+(?:\.\d+)?)px",
            scale_font,
            result,
            flags=re.IGNORECASE,
        )

    return result
