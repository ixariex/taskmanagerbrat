import json
import os
from pathlib import Path
import re

DEFAULT_SETTINGS = {
    "theme": "dark",
    "accent_color": "#A58AF5",
    "text_scale": "medium",
    "custom_colors": {},
}

VALID_THEMES = {"dark", "light", "system", "custom"}

TEXT_SCALE_FACTORS = {
    "small": 0.92,
    "medium": 1.0,
    "large": 1.10,
}

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def get_settings_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "TaskForge" / "settings.json"


def normalize_settings(settings: dict | None) -> dict:
    source = settings if isinstance(settings, dict) else {}
    normalized = dict(DEFAULT_SETTINGS)

    theme = source.get("theme", DEFAULT_SETTINGS["theme"])
    if isinstance(theme, str) and theme in VALID_THEMES:
        normalized["theme"] = theme

    scale = source.get("text_scale", DEFAULT_SETTINGS["text_scale"])
    if isinstance(scale, str) and scale in TEXT_SCALE_FACTORS:
        normalized["text_scale"] = scale

    color = str(source.get("accent_color", DEFAULT_SETTINGS["accent_color"])).strip()
    if HEX_COLOR_RE.match(color):
        normalized["accent_color"] = color.upper()

    raw_custom = source.get("custom_colors", {})
    clean_custom: dict[str, str] = {}
    if isinstance(raw_custom, dict):
        for key, val in raw_custom.items():
            if isinstance(key, str) and isinstance(val, str) and HEX_COLOR_RE.match(val.strip()):
                clean_custom[key] = val.strip().upper()
    normalized["custom_colors"] = clean_custom

    return normalized


def load_settings() -> dict:
    path = get_settings_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return dict(DEFAULT_SETTINGS)
    return normalize_settings(data)


def save_settings(settings: dict) -> dict:
    normalized = normalize_settings(settings)
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )
    temporary_path.replace(path)
    return normalized
