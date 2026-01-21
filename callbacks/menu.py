"""
callbacks/menu.py
==================
מטפל בכל כפתורי התפריט (Inline Keyboard).

data (callback_data) יכול להיות:
- menu_buy
- menu_how
- menu_ui
- menu_slots
- menu_leaders
- menu_help
"""

from utils.telegram import send_message
from texts.payment import get_payment_message
from texts.how_it_works import HOW_IT_WORKS
from texts.telegram_ui import TELEGRAM_UI_EXPLAINER
from db.events import log_event
from handlers.slots import play_slots, show_leaderboard

async def menu_callback(callback):
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    chat = callback["message"]["chat"]

    log_event(user_id, "button", data)

    if data == "menu_buy":
        msg = get_payment_message()
        return await send_message(user_id, msg)

    if data == "menu_how":
        return await send_message(user_id, HOW_IT_WORKS)

    if data == "menu_ui":
        return await send_message(user_id, TELEGRAM_UI_EXPLAINER)

    if data == "menu_slots":
        return await play_slots(chat)

    if data == "menu_leaders":
        return await show_leaderboard(chat)

    if data == "menu_help":
        return await send_message(user_id, "לתמיכה: @osifeu_prog")

    return await send_message(user_id, f"נבחר: {data}")
