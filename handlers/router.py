import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")

    if text == "/start" or text == "🔙 חזרה":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "🏆 **Diamond Arcade VIP**\nהארנק שלך מתעדכן אוטומטית בכל משחק!",
            "reply_markup": {**get_reply_keyboard(), "inline_keyboard": get_main_menu('he', user_id)}
        })

    elif text == "🎮 משחקים ופרסים":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 בחר משחק וצבור XP:", 
            "reply_markup": {"inline_keyboard": get_games_menu()}
        })

    elif text == "💰 הארנק שלי":
        # לוגיקה זמנית להצגת ארנק
        msg = "💳 **הארנק הדיגיטלי שלך**\n\n💰 טוקנים: 0\n✨ נקודות (XP): 150\n\n*צבור עוד נקודות על ידי משחקים!*"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    # המשך לוגיקת AI...
    elif not text.startswith("/") and OPENAI_KEY:
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        # ... (קוד OpenAI שקיים)
