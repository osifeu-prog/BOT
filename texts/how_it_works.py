"""
how_it_works.py
===============
HE: תקציר טקסטואלי על איך הבוט עובד (לשימוש מהיר).
EN: Short textual summary of how the bot works (for quick use).
"""

from utils.i18n import LanguageCode, t

def get_how_it_works(lang: LanguageCode) -> str:
    return t(
        lang,
        he=(
            "כאן תקבל תקציר על איך הבוט עובד ברמת זרימה:\n"
            "משתמש → טלגרם → Webhook → FastAPI → Handlers → DB → תשובה.\n\n"
            "בקורס המלא תראה דיאגרמות, קוד מלא והסברים על כל שלב."
        ),
        en=(
            "Here is a short summary of how the bot works:\n"
            "User → Telegram → Webhook → FastAPI → Handlers → DB → Response.\n\n"
            "In the full course you'll see diagrams, full code and explanations for each step."
        )
    )
