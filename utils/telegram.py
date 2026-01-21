"""
telegram.py
===========
HE: עטיפה פשוטה ל-Telegram Bot API (שליחת הודעות וקבצים).
EN: Simple wrapper around Telegram Bot API (sending messages and documents).
"""

import requests
from utils.config import TELEGRAM_API_URL
from utils.edu_log import edu_step, edu_success, edu_error

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    """
    HE: שולח הודעת טקסט למשתמש.
    EN: Sends a text message to the user.
    """
    edu_step(1, f"Sending message to chat_id={chat_id}")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode
    resp = requests.post(url, json=payload)
    if resp.ok:
        edu_success("Message sent successfully.")
    else:
        edu_error(f"Failed to send message: {resp.text}")

def send_document(chat_id, file_url, caption=None):
    """
    HE: שולח מסמך (לינק לקובץ) למשתמש.
    EN: Sends a document (file URL) to the user.
    """
    edu_step(1, f"Sending document to chat_id={chat_id}")
    url = f"{TELEGRAM_API_URL}/sendDocument"
    payload = {
        "chat_id": chat_id,
        "document": file_url,
    }
    if caption:
        payload["caption"] = caption
    resp = requests.post(url, json=payload)
    if resp.ok:
        edu_success("Document sent successfully.")
    else:
        edu_error(f"Failed to send document: {resp.text}")
