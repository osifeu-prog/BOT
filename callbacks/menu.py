from utils.telegram import send_message
from texts.payment import get_payment_message
from texts.how_it_works import HOW_IT_WORKS
from texts.telegram_ui import TELEGRAM_UI_EXPLAINER
from buttons.menus import get_course_menu
from db.events import log_event
from handlers.slots import play_slots, show_leaderboard

async def menu_callback(callback):
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    chat = callback["message"]["chat"]

    log_event(user_id, "button", data)

    if data == "menu_buy":
        return await send_message(user_id, get_payment_message())

    if data == "menu_course":
        # שולח תפריט קורס
        reply_markup = {"inline_keyboard": get_course_menu()}
        return await send_message(user_id, "📚 בחר שיעור מתוך הקורס:", reply_markup=reply_markup)

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
