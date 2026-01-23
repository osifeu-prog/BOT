import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
# פונקציית עזר לשליחת הדוח מה-router
from handlers.router import send_admin_report

async def handle_callback(callback_query):
    data = callback_query.get("data", "")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = callback_query.get("from", {}).get("id")
    call_id = callback_query.get("id")

    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": call_id})

    if data == "admin_report" and str(user_id) == str(ADMIN_ID):
        send_admin_report(chat_id)
    
    # ... שאר הקוד של ה-callbacks ...
