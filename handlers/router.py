import requests
import json
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import update_user_economy

async def handle_message(message):
    try:
        user_id = str(message.get("from", {}).get("id"))
        text = message.get("text", "")
        
        # פקודת כרייה לאדמין
        if text == "/master_mine" and user_id == str(ADMIN_ID):
            update_user_economy(user_id, slh_add=1000000)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "💰 **כרייה הושלמה:** מיליון נקודות נוספו לארנק המאסטר."})
            return

        if text == "/start":
            update_user_economy(user_id, slh_add=0)
            
            # בנייה מפורשת של המקלדת בפורמט שטלגרם אוהבת
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
                "text": "💎 **Diamond VIP Arcade**\nברוך הבא למערכת המשודרגת.\nכל היתרות מאובטחות והגנות מפני זיופים פעילות.",
                "reply_markup": keyboard # שליחת המילון ישירות
            }
            
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            
    except Exception as e:
        print(f"❌ Error: {e}")