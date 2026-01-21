"""
router.py
=========
HE: מנתב הודעות טקסט לפונקציות המתאימות (start, admin, וכו').
EN: Routes text messages to the appropriate handlers (start, admin, etc.).
"""

from utils.telegram import send_message
from db.events import log_event
from handlers.admin import admin_handler
from buttons.menus import get_main_menu
from utils.i18n import detect_language_from_telegram, t

async def handle_message(message: dict):
    """
    HE: נקודת הכניסה לכל הודעת טקסט מהמשתמש.
    EN: Entry point for every text message from the user.
    """
    user_id = message["from"]["id"]
    text = message.get("text", "") or ""
    language_code = message["from"].get("language_code")
    lang = detect_language_from_telegram(language_code)

    log_event(user_id, "message", text)

    # HE: פקודת אדמין
    # EN: Admin command
    if text.startswith("/admin"):
        return await admin_handler(message, lang)

    # HE: התחלה /start
    # EN: Start command
    if text.startswith("/start"):
        reply_markup = {"inline_keyboard": get_main_menu(lang)}
        welcome_text = t(
            lang,
            he=f"ברוך הבא {message['from'].get('first_name', '')}! מה תרצה לעשות?",
            en=f"Welcome {message['from'].get('first_name', '')}! What would you like to do?"
        )
        return send_message(user_id, welcome_text, reply_markup=reply_markup)

    # HE: ברירת מחדל — הודעה כללית
    # EN: Default fallback message
    default_text = t(
        lang,
        he="קיבלתי את ההודעה שלך.",
        en="I received your message."
    )
    return send_message(user_id, default_text)
