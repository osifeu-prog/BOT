"""
utils/telegram.py
==================
שכבת תקשורת עם Telegram API.

מטרתו:
- לספק פונקציות נוחות לשליחת הודעות ותמונות.
- להסתיר את פרטי ה-HTTP מהקוד הלוגי (handlers).
"""
import requests
from utils.config import TELEGRAM_API_URL

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode
    requests.post(url, json=payload)

def send_document(chat_id, file_url, caption=None):
    url = f"{TELEGRAM_API_URL}/sendDocument"
    payload = {
        "chat_id": chat_id,
        "document": file_url,
    }
    if caption:
        payload["caption"] = caption
    requests.post(url, json=payload)
