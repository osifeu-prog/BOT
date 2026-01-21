from utils.telegram import send_message
from db.events import log_event

async def menu_callback(callback):
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    log_event(user_id, "button", data)

    await send_message(user_id, f"נבחר: {data}")
