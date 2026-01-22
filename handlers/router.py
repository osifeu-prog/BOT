import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from buttons.menus import get_main_menu
from db.users import update_user_economy

async def handle_message(message):
    try:
        user_id = str(message.get("from", {}).get("id"))
        text = message.get("text", "")
        
        print(f"📩 Received message from {user_id}: {text}")

        if text == "/master_mine":
            if user_id == str(ADMIN_ID):
                update_user_economy(user_id, slh_add=1000000, xp_add=10000, bal_add=5000)
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                    "chat_id": user_id, 
                    "text": "👑 **ADMIN OVERRIDE**\nהוטענו 1,000,000 SLH!"
                })
            else:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🚫 גישה נדחתה."})
            return

        if text == "/start":
            # הוספת יוזר ל-DB
            update_user_economy(user_id, slh_add=0)
            
            payload = {
                "chat_id": user_id, 
                "text": "💎 **Diamond VIP Arcade**\nהמערכת מחוברת!\nבחר אופציה מהתפריט:",
                "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
            }
            r = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            print(f"📤 Sent response to {user_id}: {r.status_code}")
            
    except Exception as e:
        print(f"❌ Error in handle_message: {e}")