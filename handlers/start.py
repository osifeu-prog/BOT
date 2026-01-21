from utils.telegram import send_message
from texts.messages import TEXTS
from buttons.menus import BUTTONS
from db.events import log_event

async def start_handler(chat):
    user_id = chat["id"]
    name = chat.get("first_name", "חבר")

    log_event(user_id, "command", "/start")

    text = TEXTS["welcome"].format(name=name)
    reply_markup = {"inline_keyboard": [BUTTONS["main_menu"]]}

    await send_message(user_id, text, reply_markup=reply_markup)
