import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import get_total_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        # תפריט המשתמש הרגיל (השארנו אותו כפי שהוא)
        msg = "💎 **DIAMOND ELITE PRO**\nבחר פעולה מהתפריט:"
        kb = { "inline_keyboard": [
            [{"text": "🎮 פתח ארקייד", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI אנליסט", "callback_data": "ai_chat"}],
            [{"text": "⚙️ פאנל ניהול", "callback_data": "admin_report"}] if str(user_id) == str(ADMIN_ID) else []
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif (text == "/admin" or text == "admin") and str(user_id) == str(ADMIN_ID):
        send_admin_report(chat_id)

def send_admin_report(chat_id):
    stats = get_total_stats()
    
    report = (
        "📊 **דוח סטטוס אימפריה - Diamond Elite**\n"
        "------------------------------------\n"
        f"👤 **משתמשים:** {stats[0]}\n"
        f"💰 **מחזור SLH:** {stats[1]:,}\n\n"
        "🌐 **מצב רכיבים:**\n"
        "● שרת ליבה: 🟢 Active\n"
        "● מסד נתונים: 🟢 Connected\n"
        "● מיני-אפ: 🟢 Live\n"
        "● מנוע AI: 🟢 Ready\n\n"
        "🛠 **פעולות מהירות:**"
    )
    
    kb = { "inline_keyboard": [
        [{"text": "📥 הורד גיבוי DB", "callback_data": "admin_backup"}],
        [{"text": "📢 הודעה גלובלית", "callback_data": "broadcast_setup"}],
        [{"text": "🔄 רענן נתונים", "callback_data": "admin_report"}]
    ]}
    
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        "chat_id": chat_id, 
        "text": report, 
        "reply_markup": kb, 
        "parse_mode": "Markdown"
    })
