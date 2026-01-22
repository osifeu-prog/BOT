import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import update_user_economy

async def handle_message(message):
    try:
        user_id = str(message.get("from", {}).get("id"))
        text = message.get("text", "")
        
        if text == "/master_mine" and user_id == str(ADMIN_ID):
            update_user_economy(user_id, slh_add=1000000)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "💰 **ADMIN:** כרית 1,000,000 SLH!"})
            return

        if text == "/start":
            update_user_economy(user_id, slh_add=0)
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎮 משחקים", "callback_data": "games"}, {"text": "💰 ארנק", "callback_data": "wallet"}],
                    [{"text": "🏆 מובילים", "callback_data": "leaderboard"}, {"text": "⚙️ הגדרות", "callback_data": "settings"}]
                ]
            }
            
            if user_id == str(ADMIN_ID):
                keyboard["inline_keyboard"].append([{"text": "🛡 פאנל ניהול", "callback_data": "admin_panel"}])

            payload = {
                "chat_id": user_id,
                "text": "💎 **Diamond VIP Arcade**\nהמערכת אותחלה וסונכרנה בהצלחה.\nכל ההגנות נגד זליגות XP פעילות.",
                "reply_markup": keyboard
            }
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            
    except Exception as e:
        print(f"❌ Router Error: {e}")