import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET

async def handle_callback(callback_query):
    try:
        data = callback_query.get("data", "")
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        callback_id = callback_query.get("id")
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_id})

        if data == "buy_bot":
            msg = "🚀 **מעוניין בבוט כזה משלך?**\nהמערכת כוללת Mini-App, AI, וניהול ארנק.\n\nלפרטים ורכישה פנה לאדמין או השתמש בכפתור התשלום."
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
            
        elif data == "payment_info":
            msg = f"💳 **פרטי תשלום**\n\nניתן להעביר תשלום ב-TON לארנק הבא:\n{TON_WALLET}\n\nלאחר ההעברה שלח צילום מסך לתמיכה."
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
            
        # ... שאר הקוד הקיים (wallet, leaderboard וכו')
    except Exception as e:
        print(f"❌ Callback Error: {e}")