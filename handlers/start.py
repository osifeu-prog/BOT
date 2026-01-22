"""
handlers/start.py
==================
מטפל בפקודת /start.

מטרתו:
- לרשום אירוע ב-DB
- לבנות טקסט פתיחה שיווקי
- לבנות תפריט כפתורים
- לשלוח תמונה + טקסט + תפריט
"""

from utils.telegram import send_photo
from texts.messages import get_welcome_text
from buttons.menus import get_main_menu
from utils.config import START_PHOTO_URL
from db.events import log_event

async def start_handler(chat):
    user_id = chat["id"]
    name = chat.get("first_name", "חבר")
    lang = chat.get("language_code", "he")

    log_event(user_id, "command", "/start")

    text = get_welcome_text(lang, name)
    reply_markup = {"inline_keyboard": [get_main_menu(lang)]}

    await send_photo(user_id, START_PHOTO_URL, caption=text, reply_markup=reply_markup)
