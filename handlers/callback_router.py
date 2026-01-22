import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET, ADMIN_USERNAME, PRICE_SH

async def handle_callback(callback_query):
    user_id = callback_query.get("from", {}).get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})

    if data == "payment_info":
        # הודעה 1: כותרת
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, 
            "text": f"💳 **פרטי רכישה (מחיר: {PRICE_SH} TON)**\nהעתק את הכתובת למטה:", 
            "parse_mode": "Markdown"
        })
        # הודעה 2: הארנק (בבלוק קוד להעתקה קלה)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, 
            "text": f"{TON_WALLET}", 
            "parse_mode": "Markdown"
        })
        # הודעה 3: הנחיות
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, 
            "text": "✅ לאחר ההעברה, שלח צילום מסך ל-@" + ADMIN_USERNAME, 
            "parse_mode": "Markdown"
        })
