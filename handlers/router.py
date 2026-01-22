import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text.startswith("/start"):
        ref_id = text.split(" ")[1] if len(text.split(" ")) > 1 else None
        msg = (f"💎 **DIAMOND ELITE v7.0**\n\n"
               f"הלינק האישי שלך:\n	.me/YourBotName?start={user_id}\n\n"
               "בחר פעולה מהתפריט המקצועי:")
        kb = { "inline_keyboard": [
            [{"text": "🎮 פתח ארקייד Pro", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI אנליסט", "callback_data": "ai_chat"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
            [{"text": "👥 מערכת שותפים", "callback_data": "ref_system"}, {"text": "👤 פרופיל", "callback_data": "profile"}],
            [{"text": "📊 דאשבורד מנהל", "callback_data": "admin_report"}] if str(user_id) == str(ADMIN_ID) else []
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = callback_query.get("from", {}).get("id")
    data = callback_query.get("data", "")
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query['id']})

    if data == "admin_report":
        from db.users import get_total_stats
        s = get_total_stats()
        report = f"📊 **דוח מערכת:**\n👤 משתמשים: {s[0]}\n💰 מחזור: {s[1]}\n🌐 סטטוס: Active"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": report})
    elif data == "ai_chat":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 אני מקשיב. שאל אותי על ביטקוין, איתריום או סנטימנט השוק:"})
