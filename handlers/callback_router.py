import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET, ADMIN_USERNAME, PRICE_SH

async def handle_callback(callback_query):
    user_id = callback_query.get("from", {}).get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})

    if data == "payment_info":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💳 **פרטי רכישה:**\nהעתק את הכתובת למטה:", "parse_mode": "Markdown"})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"{TON_WALLET}", "parse_mode": "Markdown"})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ לאחר ההעברה, שלח צילום מסך לאדמין.", "parse_mode": "Markdown"})
    
    elif data == "ai_chat":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **מצב AI פעיל!**\nשאל אותי כל דבר על שוק ההון..."})