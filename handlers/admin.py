from utils.telegram import send_message
from utils.config import ADMIN_PASSWORD, ADMIN_ID
from db.admins import add_admin, is_admin

async def admin_handler(message):
    chat = message["chat"]
    user_id = chat["id"]
    text = message.get("text", "")

    parts = text.split(" ", 1)
    if len(parts) < 2:
        return await send_message(user_id, "יש להזין סיסמה: /admin <password>")

    password = parts[1].strip()

    # אם זה המנהל הראשי — תמיד מאושר
    if user_id == ADMIN_ID:
        add_admin(user_id)
        return await send_message(user_id, "הוגדרת כמנהל ראשי.")

    # בדיקת סיסמה
    if password == ADMIN_PASSWORD:
        add_admin(user_id)
        return await send_message(user_id, "הוספת כמנהל בהצלחה!")

    return await send_message(user_id, "סיסמה שגויה.")
