import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, TON_WALLET

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        msg = "👑 **DIAMOND ELITE SYSTEM v3.0**\n\nברוך הבא למערכת הניהול, הארקייד וה-AI.\nכל הכלים שלך זמינים כאן:"
        kb = {
            "inline_keyboard": [
                [{"text": "🎮 כניסה לארקייד Pro", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
                [{"text": "🤖 עוזר AI (שוק ההון)", "callback_data": "ai_chat"}, {"text": "🏆 מובילים", "callback_data": "show_leaderboard"}],
                [{"text": "💳 רכישת SLH", "callback_data": "payment_info"}, {"text": "👤 הפרופיל שלי", "callback_data": "user_profile"}],
                [{"text": "💼 כרטיס ביקור דיגיטלי", "callback_data": "biz_card"}]
            ]
        }
        if str(user_id) == str(ADMIN_ID):
            kb["inline_keyboard"].append([{"text": "⚙️ פאנל אדמין מורחב", "callback_data": "admin_main"}])
            
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})
