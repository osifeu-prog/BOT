"""
menu.py
=======
HE: טיפול בכפתורי התפריט הראשי.
EN: Handling main menu buttons.
"""

from utils.telegram import send_message
from texts.payment import get_payment_message
from texts.how_it_works import get_how_it_works
from texts.telegram_ui import get_telegram_ui_explainer
from buttons.menus import get_course_menu
from db.events import log_event
from handlers.slots import play_slots, show_leaderboard
from utils.config import SUPPORT_CONTACT_TEXT_HE, SUPPORT_CONTACT_TEXT_EN
from utils.i18n import detect_language_from_telegram, t
from utils.edu_log import edu_step, edu_path

async def menu_callback(callback: dict):
    """
    HE: מטפל בכל כפתורי menu_*.
    EN: Handles all menu_* buttons.
    """
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    language_code = callback["from"].get("language_code")
    lang = detect_language_from_telegram(language_code)

    edu_path("USER → CALLBACK → MENU")
    edu_step(1, f"Menu callback: {data!r} from user {user_id}")

    log_event(user_id, "button", data)

    if data == "menu_buy":
        return send_message(user_id, get_payment_message(lang))

    if data == "menu_course":
        reply_markup = {"inline_keyboard": get_course_menu(lang)}
        return send_message(
            user_id,
            t(lang, "📚 בחר שיעור מתוך הקורס:", "📚 Choose a lesson from the course:"),
            reply_markup=reply_markup
        )

    if data == "menu_how":
        return send_message(user_id, get_how_it_works(lang))

    if data == "menu_ui":
        return send_message(user_id, get_telegram_ui_explainer(lang))

    if data == "menu_slots":
        return await play_slots(callback["message"]["chat"], lang)

    if data == "menu_leaders":
        return await show_leaderboard(callback["message"]["chat"], lang)

    if data == "menu_help":
        text = t(
            lang,
            he="לתמיכה ויצירת קשר בכל שלב:\n" + SUPPORT_CONTACT_TEXT_HE,
            en="For support and contact at any stage:\n" + SUPPORT_CONTACT_TEXT_EN
        )
        return send_message(user_id, text)

    return send_message(
        user_id,
        t(lang, f"נבחר: {data}", f"Selected: {data}")
    )
