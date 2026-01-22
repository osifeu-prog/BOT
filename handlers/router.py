import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import get_total_stats, get_leaderboard

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        msg = "👑 **Diamond VIP Elite System**\n\nברוך הבא למערכת היוקרה. בחר פעולה מהתפריט:"
        kb = {
            "inline_keyboard": [
                [{"text": "🎮 כניסה לארקייד Pro", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
                [{"text": "🏆 טבלת מובילים", "callback_data": "show_leaderboard"}, {"text": "🤖 ניתוח AI", "callback_data": "ai_analysis"}],
                [{"text": "💳 רכישת SLH", "callback_data": "payment_info"}]
            ]
        }
        if str(user_id) == str(ADMIN_ID):
            kb["inline_keyboard"].append([{"text": "⚙️ פאנל ניהול", "callback_data": "admin_main"}])
            
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif text == "/admin" and str(user_id) == str(ADMIN_ID):
        stats = get_total_stats()
        admin_msg = f"📊 **נתוני מערכת:**\n👥 משתמשים: {stats[0]}\n💰 מחזור SLH: {stats[1]}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": admin_msg})
