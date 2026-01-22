import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import get_total_stats, get_user_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text.startswith("/start"):
        # בדיקה אם המשתמש הגיע דרך לינק הזמנה (Referral)
        referrer_id = text.split(" ")[1] if len(text.split(" ")) > 1 else None
        
        msg = "💎 **DIAMOND ELITE PRO v5.0**\n\nברוך הבא למערכת.\nהלינק האישי שלך להזמנת חברים:\n	.me/bot-production-2668.up.railway.app?start={user_id}"
        kb = { "inline_keyboard": [
            [{"text": "🎮 פתח ארקייד", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "📊 דוח מנהל", "callback_data": "admin_report"}] if str(user_id) == str(ADMIN_ID) else [{"text": "🏆 מובילים", "callback_data": "leaderboard"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif text == "/admin" and str(user_id) == str(ADMIN_ID):
        send_admin_report(chat_id)

def send_admin_report(chat_id):
    stats = get_total_stats()
    report = f"📊 **דוח מנהל חי:**\n\n👤 משתמשים: {stats[0]}\n💰 מחזור SLH: {stats[1]}\n🟢 מערכת: Active"
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": report})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = callback_query.get("from", {}).get("id")
    data = callback_query.get("data", "")
    
    # אישור לחיצה חובה למניעת "שעון מסתובב"
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query['id']})

    if data == "admin_report" and str(user_id) == str(ADMIN_ID):
        send_admin_report(chat_id)
    elif data == "leaderboard":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🏆 טבלת המובילים בטעינה..."})
