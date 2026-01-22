import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, PARTICIPANTS_GROUP_LINK, TEST_GROUP_LINK

async def handle_message(message):
    try:
        user_id = message.get("from", {}).get("id")
        user_id_str = str(user_id)
        text = message.get("text", "")
        
        if text == "/start":
            keyboard = [
                [{"text": "🎮 כניסה ל-Diamond VIP (Mini-App)", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
                [{"text": "💰 ארנק", "callback_data": "wallet"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
                [{"text": "👥 קבוצת חברים", "url": PARTICIPANTS_GROUP_LINK}, {"text": "🛡️ קבוצת תמיכה", "url": TEST_GROUP_LINK}],
                [{"text": "🤖 רכישת בוט כזה", "callback_data": "buy_bot"}, {"text": "💳 העברת תשלום", "callback_data": "payment_info"}],
                [{"text": "⚙️ הגדרות", "callback_data": "settings"}]
            ]
            
            if user_id_str == str(ADMIN_ID):
                keyboard.append([{"text": "🔒 פאנל ניהול אדמין", "callback_data": "admin_panel"}])

            payload = {
                "chat_id": user_id,
                "text": "💎 **Diamond VIP Arcade**\nברוך הבא למערכת הסנכרון המלאה.\nבחר את הפעולה הרצויה:",
                "reply_markup": {"inline_keyboard": keyboard}
            }
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
    except Exception as e:
        print(f"❌ Router Error: {e}")