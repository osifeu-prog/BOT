from handlers.start import start_handler
from handlers.echo import echo_handler
from utils.config import ALLOWED_USERS
from db.events import log_event

async def handle_message(message):
    chat = message["chat"]
    user_id = chat["id"]
    text = message.get("text", "")

    if user_id not in ALLOWED_USERS:
        return

    log_event(user_id, "message", text or "")

    if text == "/start":
        return await start_handler(chat)

    return await echo_handler(message)
