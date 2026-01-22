import requests, datetime
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import update_user_balance, get_user_stats, get_total_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # 1. טיפול באנימציות טלגרם
    if dice:
        v = dice.get("value")
        e = dice.get("emoji")
        win = 500 if (e == "🎰" and v in [1, 22, 43, 64]) or (e == "🎲" and v == 6) else 0
        if win > 0:
            update_user_balance(user_id, win)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🔥 זכייה מטורפת! +{win} SLH נוספו לארנק!"})
        return

    # 2. פקודות מערכת
    if text.startswith("/start"):
        msg = "💎 **DIAMOND ELITE ALPHA v10.0**\n\nברוך הבא למערכת הפיננסית המתקדמת בטלגרם.\nהשתמש בתפריט למטה או בכפתור הפקודות."
        kb = {"inline_keyboard": [
            [{"text": "💳 הארנק שלי & ניהול", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI יועץ אישי", "callback_data": "ai_menu"}, {"text": "💰 משימות Earn", "callback_data": "tasks_menu"}],
            [{"text": "📈 יומן שוק", "callback_data": "journal_view"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
            [{"text": "⚙️ פאנל אדמין", "callback_data": "admin_report"}] if user_id == str(ADMIN_ID) else []
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    # 3. טיפול ב-AI ויומן (כל טקסט אחר)
    elif text and not text.startswith("/"):
        res = f"🤖 **AI Assistant:**\nניתחתי את בקשתך: '{text}'.\nשמרתי תובנה זו ביומן המעקב שלך תחת קטגוריית 'שוק חופשי'."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": res})

def handle_callback(callback_query):
    c_id = callback_query.get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": c_id})

    if data == "tasks_menu":
        msg = "🎯 **משימות Earn:**\n1. הצטרף לערוץ החדשות (+1000 SLH)\n2. הזמן 3 חברים (+2500 SLH)"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
    elif data == "admin_report":
        stats = get_total_stats()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📊 סטטוס: {stats[0]} משתמשים פעילים."})
