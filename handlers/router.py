import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, BOT_USERNAME, PRICE_SH
from buttons.menus import get_main_menu
from db.users import add_user

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    if text.startswith("/start"):
        add_user(user_id)
        # שימוש בטקסט פשוט לניסיון ראשון כדי לוודא שזה עובד
        msg = f"🏆 VIP TRADING BOT\n\nברוך הבא! המערכת מוכנה.\n\nמחיר: {PRICE_SH}"
        menu = get_main_menu("he", user_id)
        
        payload = {
            "chat_id": user_id, 
            "text": msg, 
            "reply_markup": {"inline_keyboard": menu}
        }
        r = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        print(f"📤 Send Status: {r.json()}") # יראה לנו אם טלגרם חסמה את ההודעה
