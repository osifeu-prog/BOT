from utils.telegram import send_message
from db.events import log_event
from db.admins import is_admin
from db.buyers import is_buyer
from handlers.admin import admin_handler
from buttons.menus import get_main_menu, get_buyer_menu
from utils.i18n import detect_language_from_telegram, t
from utils.edu_log import edu_path

async def handle_message(message: dict):
    user_id = message["from"]["id"]
    text = message.get("text", "") or ""
    first_name = message["from"].get("first_name", "חבר")
    lang = detect_language_from_telegram(message["from"].get("language_code"))

    # לוג ראשוני
    log_event(user_id, "message", text)
    edu_path(f"MESSAGE: {text}")

    # בדיקת אדמין
    if text.startswith("/admin") or is_admin(user_id):
        if text.startswith("/admin"):
             return await admin_handler(message, lang)

    # התחלה / תפריט ראשי
    if text.startswith("/start"):
        if is_buyer(user_id):
            welcome_text = t(lang, f"ברוך הבא חזרה, {first_name}! ✨", f"Welcome back, {first_name}! ✨")
            reply_markup = {"inline_keyboard": get_buyer_menu(lang)}
        else:
            # כאן אנחנו מעבירים את ה-user_id כדי שהלינק שותפים יווצר נכון
            welcome_text = t(lang, f"שלום {first_name}! 👋", f"Hi {first_name}! 👋")
            reply_markup = {"inline_keyboard": get_main_menu(lang, user_id)}
        return send_message(user_id, welcome_text, reply_markup=reply_markup)

    fallback_text = t(lang, "אני לא בטוח שהבנתי...", "I'm not sure I got that...")
    return send_message(user_id, fallback_text)
