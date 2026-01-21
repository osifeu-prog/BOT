from utils.telegram import send_message
from texts.payment import get_payment_message
from texts.how_it_works import HOW_IT_WORKS
from texts.telegram_ui import TELEGRAM_UI_EXPLAINER
from buttons.menus import get_course_menu
from db.events import log_event
from handlers.slots import play_slots, show_leaderboard
from utils.config import SUPPORT_CONTACT_TEXT

async def menu_callback(callback):
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    log_event(user_id, "button", data)

    if data == "menu_buy":
        return send_message(user_id, get_payment_message())

    if data == "menu_course":
        reply_markup = {"inline_keyboard": get_course_menu()}
        return send_message(user_id, "📚 בחר שיעור מתוך הקורס:", reply_markup=reply_markup)

    if data == "menu_how":
        return send_message(user_id, HOW_IT_WORKS)

    if data == "menu_ui":
        return send_message(user_id, TELEGRAM_UI_EXPLAINER)

    if data == "menu_slots":
        return await play_slots(callback["message"]["chat"])

    if data == "menu_leaders":
        return await show_leaderboard(callback["message"]["chat"])

    if data == "menu_help":
        return send_message(
            user_id,
            "לתמיכה ויצירת קשר בכל שלב:\n" + SUPPORT_CONTACT_TEXT
        )

    return send_message(user_id, f"נבחר: {data}")
