import httpx
from utils.config import API_URL

async def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json=payload)


async def send_photo(chat_id, photo_url, caption=None):
    payload = {
        "chat_id": chat_id,
        "photo": photo_url
    }

    if caption:
        payload["caption"] = caption

    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendPhoto", json=payload)
