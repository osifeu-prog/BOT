import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def set_bot_commands():
    # הגדרת הכפתור הכחול (Menu Button)
    commands = [
        {"command": "start", "description": "💎 תפריט ראשי"},
        {"command": "ai", "description": "🤖 עוזר AI אישי"},
        {"command": "games", "description": "🎮 מרכז המשחקים"},
        {"command": "profile", "description": "👤 הפרופיל שלי"},
        {"command": "wallet", "description": "💳 ארנק ו-SLH"},
        {"command": "help", "description": "❓ עזרה ותמיכה"}
    ]
    requests.post(f"{TELEGRAM_API_URL}/setMyCommands", json={"commands": commands})

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        set_bot_commands()
        msg = "👑 **WELCOME TO DIAMOND ELITE PRO**\n\nהעוזר האישי שלך מוכן. הכל זמין בתפריט למטה או בכפתורים:"
        kb = { "inline_keyboard": [
            [{"text": "🎮 שחק עכשיו", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI עוזר אישי", "callback_data": "ai_chat"}, {"text": "📝 יומן מעקב שוק", "callback_data": "ai_journal"}],
            [{"text": "💳 הארנק שלי", "callback_data": "wallet"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
            [{"text": "⚙️ פאנל ניהול", "callback_data": "admin_report"}] if str(user_id) == str(ADMIN_ID) else []
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif text == "/ai" or "מצב" in text or "ביטקוין" in text:
        # כאן ה-AI עונה (סימולציה כרגע, אפשר לחבר ל-OpenAI/Gemini API)
        response = "🤖 **ניתוח שוק נוכחי:**\nהביטקוין מראה יציבות מעל . מגמת הסנטימנט חיובית. מומלץ לעקוב אחרי רמות תמיכה ב-TON."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": response, "parse_mode": "Markdown"})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query['id']})

    if data == "ai_chat":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **אני כאן בשבילך.**\nשאל אותי הכל, צור איתי יומן מעקב או בקש ניתוח טרנדים."})
    elif data == "wallet":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💳 **סטטוס ארנק:**\nיתרה: 0 SLH\nכתובת TON: לא מחובר"})
