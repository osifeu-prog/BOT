from utils.telegram import send_message, send_photo
from texts.messages import TEXTS
from buttons.menus import BUTTONS
from utils.photos import START_PHOTO_URL
from db.events import log_event

async def start_handler(chat):
    user_id = chat["id"]
    name = chat.get("first_name", "חבר")

    log_event(user_id, "command", "/start")

    # שליחת תמונה
    await send_photo(user_id, START_PHOTO_URL)

    # שליחת טקסט + תפריט
    text = TEXTS["welcome"].format(name=name)
    reply_markup = {"inline_keyboard": [BUTTONS["main_menu"]]}

    await send_message(user_id, text, reply_markup=reply_markup)
