import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import get_total_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        msg = "💎 **DIAMOND ELITE PRO v4.0**\n\nהמערכת המלאה מוכנה עבורך."
        kb = { "inline_keyboard": [
            [{"text": "🎮 פתח ארקייד & משימות", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI אנליסט", "callback_data": "ai_chat"}, {"text": "🏆 טבלת מובילים", "callback_data": "show_leaderboard"}],
            [{"text": "👤 הפרופיל שלי", "callback_data": "user_profile"}, {"text": "💰 רכישת SLH", "callback_data": "payment_info"}],
            [{"text": "⚙️ פאנל ניהול", "callback_data": "admin_main"}] if str(user_id) == str(ADMIN_ID) else []
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif text == "/admin" and str(user_id) == str(ADMIN_ID):
        s = get_total_stats()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📊 **מצב מערכת:**\n\n👤 משתמשים: {s[0]}\n💰 מחזור SLH: {s[1]}"})
