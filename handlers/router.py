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
            
            # מקלדת בפורמט רשימה פשוטה
            keyboard = [
                [{"text": "🎮 משחקים", "callback_data": "games"}, {"text": "💰 ארנק", "callback_data": "wallet"}],
                [{"text": "🏆 מובילים", "callback_data": "leaderboard"}, {"text": "⚙️ הגדרות", "callback_data": "settings"}]
            ]
            
            if user_id_str == str(ADMIN_ID):
                keyboard.append([{"text": "🛡 פאנל ניהול", "callback_data": "admin_panel"}])

            payload = {
                "chat_id": user_id,
                "text": "💎 **Diamond VIP Arcade**\nהמערכת סונכרנה.\nהשתמש בכפתורים למטה:",
                "reply_markup": {"inline_keyboard": keyboard}
            }
            
            resp = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            print(f"📤 Telegram Send Status: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"❌ Router Error: {e}")