from utils.telegram import send_message
from utils.i18n import detect_language_from_telegram, t
from buttons.menus import get_main_menu, get_buyer_menu
from db.buyers import is_buyer
from db.events import log_event
from db.users import add_user
from handlers.admin import admin_handler

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")
    lang = detect_language_from_telegram(message["from"].get("language_code"))
    
    log_event(user_id, "message", text)
    
    if text.startswith("/admin"):
        await admin_handler(message)
        return

    if text.startswith("/start"):
        # בדיקת שותפים
        parts = text.split()
        referrer = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
        if referrer and int(referrer) != user_id:
            add_user(user_id, int(referrer))
        else:
            add_user(user_id)
            
        if is_buyer(user_id):
            menu = get_buyer_menu(lang)
            txt = t(lang, "ברוך שובך!", "Welcome back!")
        else:
            menu = get_main_menu(lang, user_id)
            txt = t(lang, "ברוך הבא לבוט!", "Welcome!")
            
        send_message(user_id, txt, {"inline_keyboard": menu})
