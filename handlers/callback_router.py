import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET, ADMIN_ID

async def handle_callback(callback_query):
    user_id = callback_query.get("from", {}).get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")

    if data == "ref_link":
        link = f"https://t.me/share/url?url=https://t.me/YOUR_BOT_USERNAME?start={user_id}&text=בוא תרוויח SLH איתי!"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🔗 **לינק ההזמנה שלך:**\n\n{link}", "parse_mode": "Markdown"})
    
    elif data == "play_dice":
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "אם יצא 6 - זכית ב-10 SLH!"})
