import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")

    if text == "/start":
        welcome_text = "👋 ברוך הבא ל-**Diamond VIP System**\n\nכאן תוכל לנהל את התיק שלך, לשחק בארקייד ולהתייעץ עם ה-AI שלנו."
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎮 פתח ארקייד", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
                [{"text": "🤖 שאל את ה-AI", "callback_data": "ai_chat"}, {"text": "💳 רכישת SLH", "callback_data": "payment_info"}],
                [{"text": "📊 סטטיסטיקות שלי", "callback_data": "user_stats"}]
            ]
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": welcome_text, "reply_markup": keyboard, "parse_mode": "Markdown"})