import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, PARTICIPANTS_GROUP_LINK, TEST_GROUP_LINK, ADMIN_USERNAME

async def handle_message(message):
    try:
        user_id = message.get("from", {}).get("id")
        user_id_str = str(user_id)
        text = message.get("text", "")

        if text == "/start":
            keyboard = [
                [{"text": "✨ כניסה לארקייד VIP", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
                [{"text": "💰 ארנק", "callback_data": "wallet"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
                [{"text": "👥 קבוצת חברים", "url": PARTICIPANTS_GROUP_LINK}],
                [{"text": "🛡️ קבוצת בדיקות", "url": TEST_GROUP_LINK}],
                [{"text": "🚀 רכישת הבוט", "callback_data": "buy_bot"}]
            ]
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": user_id, "text": "💎 **Diamond VIP Arcade**\nהמערכת מסונכרנת למשתנים שלך.",
                "reply_markup": {"inline_keyboard": keyboard}, "parse_mode": "Markdown"
            })
    except Exception as e:
        print(f"Error: {e}")