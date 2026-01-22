"""
i18n.py
========
HE: מודול לניהול שפות בבוט (עברית / אנגלית).
EN: Module for handling languages in the bot (Hebrew / English).
"""

from typing import Literal

LanguageCode = Literal["he", "en"]

def detect_language_from_telegram(language_code: str | None) -> LanguageCode:
    """
    HE: מקבל language_code מטלגרם ומחזיר 'he' או 'en' כברירת מחדל.
    EN: Takes Telegram's language_code and returns 'he' or 'en' as default.
    """
    if not language_code:
        return "he"
    if language_code.startswith("he"):
        return "he"
    return "en"

def t(lang: LanguageCode, he: str, en: str) -> str:
    """
    HE: פונקציה פשוטה לבחירת טקסט לפי שפה.
    EN: Simple helper to choose text by language.
    """
    return he if lang == "he" else en
