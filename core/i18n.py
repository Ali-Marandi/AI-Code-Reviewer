"""Trusted, packaged translation loading for the desktop application."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QLocale, Qt, QTranslator
from PySide6.QtWidgets import QApplication


SUPPORTED_LOCALES = {"en", "fa"}
DEFAULT_LOCALE = "en"


def application_root() -> Path:
    """Return the installed bundle root or the source-project root."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def normalize_locale(value: Optional[str]) -> str:
    """Accept only bundled language identifiers and safely fall back to English."""
    if not value or value.lower() == "auto":
        system_language = QLocale.system().name().split("_", 1)[0].lower()
        return system_language if system_language in SUPPORTED_LOCALES else DEFAULT_LOCALE
    locale = value.lower().split("_", 1)[0].split("-", 1)[0]
    return locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE


def install_translation(app: QApplication, requested_locale: Optional[str] = "auto") -> Optional[QTranslator]:
    """Install a translation bundled with the application, never a remote or user-supplied catalog."""
    locale = normalize_locale(requested_locale)
    app.setLayoutDirection(Qt.RightToLeft if locale == "fa" else Qt.LeftToRight)
    if locale == DEFAULT_LOCALE:
        return None

    translations_dir = application_root() / "translations"
    translator = QTranslator(app)
    if not translator.load(f"ai_code_reviewer_{locale}", str(translations_dir)):
        return None
    app.installTranslator(translator)
    return translator
