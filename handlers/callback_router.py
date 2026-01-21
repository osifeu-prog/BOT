from callbacks.menu import menu_callback
from utils.config import ALLOWED_USERS

async def handle_callback(callback):
    user_id = callback["message"]["chat"]["id"]

    if user_id not in ALLOWED_USERS:
        return

    data = callback["data"]

    if data.startswith("menu_"):
        return await menu_callback(callback)
