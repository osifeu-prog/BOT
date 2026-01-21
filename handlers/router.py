"""
handlers/router.py
===================
זה ה-"Router" הראשי של הודעות טקסט.

מטרתו:
- לקבל כל message מטלגרם
- להחליט מה לעשות איתו:
  - /admin → admin_handler
  - "אושר" → send_zip
  - /slots → play_slots
  - /leaders → show_leaderboard
  - /start → start_handler
  - כל דבר אחר → echo_handler

שימו לב:
- הבוט פתוח לכולם (לא חוסם משתמשים רגילים).
"""
from utils.telegram import send_message
from db.events import log_event
from handlers.admin import admin_handler
from buttons.menus import get_main_menu

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")

    log_event(user_id, "message", text)

    if text.startswith("/admin"):
        return await admin_handler(message)

    if text.startswith("/start"):
        reply_markup = {"inline_keyboard": get_main_menu()}
        return send_message(
            user_id,
            f"ברוך הבא {message['from'].get('first_name', '')}! מה תרצה לעשות?",
            reply_markup=reply_markup
        )

    return send_message(user_id, "קיבלתי את ההודעה שלך.")
