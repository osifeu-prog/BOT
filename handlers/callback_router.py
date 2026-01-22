import requests
from utils.config import TELEGRAM_API_URL, BOT_USERNAME

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_affiliate":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        share_url = f"https://t.me/share/url?url={ref_link}&text=בוא%20תראה%20את%20בוט%20המסחר%20החדש!%20משחקים%20ומרוויחים%20XP%20ביחד!"
        menu = [[{"text": "🚀 שלח הזמנה לחבר", "url": share_url}]]
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "🤝 **תוכנית השותפים**\nהזמן חברים וקבל XP על כל משחק שלהם!",
            "reply_markup": {"inline_keyboard": menu}
        })
