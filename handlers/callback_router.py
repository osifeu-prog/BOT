import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET, ADMIN_USERNAME, PRICE_SH, TOKEN_PACKS

async def handle_callback(callback_query):
    user_id = callback_query.get("from", {}).get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})

    if data == "payment_info":
        # הודעה 1: הסבר
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": f"🚀 **רכישת חבילה: {PRICE_SH} TON**\nבחרת לשדרג את המערכת שלך.", "parse_mode": "Markdown"
        })
        # הודעה 2: הכתובת להעתקה קלה
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": f"{TON_WALLET}", "parse_mode": "Markdown"
        })
        # הודעה 3: הוראות
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": "✅ העתק את הכתובת למעלה.\n📸 לאחר ההעברה, שלח צילום מסך לכאן.", "parse_mode": "Markdown"
        })