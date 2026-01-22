import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import update_user_economy

async def handle_message(message):
    try:
        user_id = message.get("from", {}).get("id")
        user_id_str = str(user_id)
        text = message.get("text", "")
        
        if text == "/master_mine" and user_id_str == str(ADMIN_ID):
            update_user_economy(user_id_str, slh_add=1000000)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "💰 **ADMIN:** כרית 1,000,000 SLH!"})
            return

        if text == "/start":
            update_user_economy(user_id_str, slh_add=0)
            
            keyboard = [
                [{"text": "🎮 פתח משחקים (Mini-App)", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
                [{"text": "💰 ארנק", "callback_data": "wallet"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
                [{"text": "🤖 שאל את AI", "callback_data": "ai_chat"}, {"text": "⚙️ הגדרות", "callback_data": "settings"}]
            ]
            
            if user_id_str == str(ADMIN_ID):
                keyboard.append([{"text": "🛡 פאנל ניהול", "callback_data": "admin_panel"}])

            payload = {
                "chat_id": user_id,
                "text": "💎 **Diamond VIP Arcade**\nברוך הבא למערכת המלאה.\nכל התכונות והתוספות הופעלו.",
                "reply_markup": {"inline_keyboard": keyboard}
            }
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            
    except Exception as e:
        print(f"❌ Router Error: {e}")