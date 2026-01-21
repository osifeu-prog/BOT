from handlers.start import start_handler
from handlers.echo import echo_handler
from handlers.admin import admin_handler
from db.admins import is_admin
from utils.config import ADMIN_ID

async def handle_message(message):
    chat = message["chat"]
    user_id = chat["id"]
    text = message.get("text", "")

    # פקודת מנהל
    if text.startswith("/admin"):
        return await admin_handler(message)

    # רק מנהלים יכולים להשתמש בבוט
    if not is_admin(user_id):
        return await send_message(user_id, "אין לך הרשאה להשתמש בבוט.")

    # פקודת התחלה
    if text == "/start":
        return await start_handler(chat)

    return await echo_handler(message)
