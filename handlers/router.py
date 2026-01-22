from utils.telegram import send_message
from buttons.menus import get_main_menu, get_buyer_menu
from db.users import add_user
from db.buyers import is_buyer
from db.admins import is_admin
from utils.config import ADMIN_ID
import requests
from utils.config import TELEGRAM_API_URL

async def handle_message(message):
    user_id = message["from"]["id"]
    lang = "he"
    
    # טיפול בתמונות
    if "photo" in message:
        send_message(user_id, "✅ **התמונה התקבלה!** המנהל בודק את ההעברה שלך.")
        photo_id = message["photo"][-1]["file_id"]
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json={
            "chat_id": ADMIN_ID,
            "photo": photo_id,
            "caption": f"💰 **הוכחת תשלום!**\nמאת: {user_id}\nשם: {message['from'].get('first_name')}"
        })
        return

    text = message.get("text", "")
    
    if text.startswith("/start"):
        parts = text.split()
        referrer = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
        add_user(user_id, int(referrer) if referrer else None)
        
        if is_buyer(user_id):
            send_message(user_id, "👑 **ברוך הבא ללובי ה-VIP!**", {"inline_keyboard": get_buyer_menu(lang)})
        else:
            send_message(user_id, "🔥 **מוכן להתחיל להרוויח?**", {"inline_keyboard": get_main_menu(lang, user_id)})
