import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        r = requests.post(API_URL, json=payload)
        print("Telegram response:", r.text)
        return "ok"
    except Exception as e:
        print("ERROR sending message:", e)
        return "error"
