import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from buttons.menus import get_main_menu
from db.users import update_user_economy

async def handle_message(message):
    try:
        user_id = str(message.get("from", {}).get("id"))
        text = message.get("text", "")
        
        print(f"📩 Received: {text} from {user_id}")

        if text == "/master_mine" and user_id == str(ADMIN_ID):
            update_user_economy(user_id, slh_add=1000000)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "💰 כרית 1,000,000 SLH בהצלחה!"})
            return

        if text == "/admin" and user_id == str(ADMIN_ID):
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": user_id, 
                "text": "🕶 **ADMIN TERMINAL**\nהמערכת מאובטחת. עמודות ה-DB סונכרנו.\nכל המערכות ירוקות. 🚀"
            })
            return

        if text == "/start":
            update_user_economy(user_id, slh_add=0) # זה יצור את המשתמש אם לא קיים
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": user_id, 
                "text": "💎 **Diamond VIP Arcade**\nברוך הבא! הכל עובד עכשיו.",
                "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
            })
            
    except Exception as e:
        print(f"❌ Error: {e}")