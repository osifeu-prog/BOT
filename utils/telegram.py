import requests
from utils.config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL

def send_message(chat_id, text, reply_markup=None):
    """שולח הודעת טקסט למשתמש"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def edit_message(chat_id, message_id, text, reply_markup=None):
    """עורך הודעה קיימת (שימושי למשחקים)"""
    url = f"{TELEGRAM_API_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    response = requests.post(url, json=payload)
    return response.json()
