from callbacks.menu import menu_callback
from db.admins import is_admin
from utils.config import ADMIN_ID

async def handle_callback(callback):
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    # רק מנהלים יכולים ללחוץ על כפתורים
    if not is_admin(user_id) and user_id != ADMIN_ID:
        return

    if data.startswith("menu_"):
        return await menu_callback(callback)
