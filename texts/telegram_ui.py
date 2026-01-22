"""
telegram_ui.py
==============
HE: תקציר על סוגי התפריטים בטלגרם.
EN: Short summary about Telegram UI elements.
"""

from utils.i18n import LanguageCode, t

def get_telegram_ui_explainer(lang: LanguageCode) -> str:
    return t(
        lang,
        he=(
            "בוט בטלגרם יכול להשתמש ב:\n"
            "- Reply Keyboard\n"
            "- Inline Keyboard\n"
            "- Bot Menu\n"
            "- Commands\n"
            "- WebApps\n"
            "- Attachment Menu\n\n"
            "בקורס המלא תראה דוגמאות קוד לכל אחד מהם."
        ),
        en=(
            "A Telegram bot can use:\n"
            "- Reply Keyboard\n"
            "- Inline Keyboard\n"
            "- Bot Menu\n"
            "- Commands\n"
            "- WebApps\n"
            "- Attachment Menu\n\n"
            "In the full course you'll see code examples for each of them."
        )
    )
