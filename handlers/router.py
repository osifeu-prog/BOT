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
"""

from handlers.start import start_handler
from handlers.echo import echo_handler
from handlers.admin import admin_handler
from handlers.send_zip import send_zip
from handlers.slots import play_slots, show_leaderboard
from db.admins import is_admin
from utils.config import ADMIN_ID
from utils.telegram import send_message

async def handle_message(message):
    chat = message["chat"]
    user_id = chat["id"]
    text = message.get("text", "")

    # ניסיון להפוך למנהל
    if text.startswith("/admin"):
        return await admin_handler(message)

    # אישור תשלום — שולח ZIP
    if text.lower().startswith("אושר") or text.lower().startswith("approved"):
        return await send_zip(chat)

    # משחק SLOTS
    if text == "/slots":
        return await play_slots(chat)

    # טבלת מובילים
    if text == "/leaders":
        return await show_leaderboard(chat)

    # בדיקת הרשאה — רק מנהלים (או אתה) יכולים להשתמש בבוט
    if not is_admin(user_id) and user_id != ADMIN_ID:
        return await send_message(user_id, "אין לך הרשאה להשתמש בבוט.")

    # התחלה — /start
    if text == "/start":
        return await start_handler(chat)

    # כל דבר אחר — echo
    return await echo_handler(message)
