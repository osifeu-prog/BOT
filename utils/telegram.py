"""
utils/telegram.py
==================
שכבת תקשורת עם Telegram API.

מטרתו:
- לספק פונקציות נוחות לשליחת הודעות ותמונות.
- להסתיר את פרטי ה-HTTP מהקוד הלוגי (handlers).
"""

import httpx
from utils.config import API_URL

async def send_message(chat_id, text, reply_markup=None):
    """
    שולח הודעת טקסט למשתמש.

    chat_id — מזהה הצ'אט (בדרך כלל user_id)
    text — הטקסט שנשלח למשתמש
    reply_markup — תפריט כפתורים (Inline Keyboard) אם יש
    """
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json=payload)


async def send_photo(chat_id, photo_url, caption=None, reply_markup=None):
    """
    שולח תמונה למשתמש.

    photo_url — קישור לתמונה (למשל מ-GitHub assets)
    caption — טקסט מתחת לתמונה
    reply_markup — תפריט כפתורים (Inline Keyboard) אם יש
    """
    payload = {
        "chat_id": chat_id,
        "photo": photo_url
    }
    if caption:
        payload["caption"] = caption
        payload["parse_mode"] = "Markdown"
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendPhoto", json=payload)
