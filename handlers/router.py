import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import get_total_stats, get_user_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text.startswith("/start"):
        msg = "👑 **DIAMOND ELITE SYSTEM v6.0**\n\nברוך הבא למוצר המלא. המערכת כוללת ארקייד, AI וניהול נכסים."
        kb = { "inline_keyboard": [
            [{"text": "🎮 כניסה לארקייד Pro", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI אנליסט", "callback_data": "ai_chat"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
            [{"text": "👤 פרופיל & שותפים", "callback_data": "user_profile"}]
        ]}
        if str(user_id) == str(ADMIN_ID):
            kb["inline_keyboard"].append([{"text": "📊 דאשבורד ניהול", "callback_data": "admin_report"}])
            
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = callback_query.get("from", {}).get("id")
    data = callback_query.get("data", "")
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query['id']})

    if data == "admin_report" and str(user_id) == str(ADMIN_ID):
        s = get_total_stats()
        report = f"📊 **דוח מערכת מלא:**\n\n👤 משתמשים: {s[0]}\n💰 מחזור: {s[1]}\n⚙️ AI: Active\n🌐 WebApp: Online"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": report})
    elif data == "ai_chat":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 שלח לי שם של מטבע או שאלה על השוק:"})
