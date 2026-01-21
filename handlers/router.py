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

    if text.startswith("/admin"):
        return await admin_handler(message)

    if text.lower().startswith("אושר") or text.lower().startswith("approved"):
        return await send_zip(chat)

    if text == "/slots":
        return await play_slots(chat)

    if text == "/leaders":
        return await show_leaderboard(chat)

    if not is_admin(user_id) and user_id != ADMIN_ID:
        return await send_message(user_id, "אין לך הרשאה להשתמש בבוט.")

    if text == "/start":
        return await start_handler(chat)

    return await echo_handler(message)
