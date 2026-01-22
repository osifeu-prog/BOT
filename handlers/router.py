import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import get_total_stats, get_all_users

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if text == "/admin" and str(user_id) == str(ADMIN_ID):
        stats = get_total_stats()
        msg = f"📊 **פאנל ניהול ראשי**\n\n👤 משתמשים רשומים: {stats[0]}\n💰 סך SLH במערכת: {stats[1]}\n\nבחר פעולה:"
        kb = {
            "inline_keyboard": [
                [{"text": "📢 הודעה לכל המשתמשים", "callback_data": "broadcast_setup"}],
                [{"text": "🎁 חלוקת בונוס גלובלי", "callback_data": "global_bonus"}]
            ]
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})
    
    # ... שאר הקוד של ה-router שכתבנו קודם ...
