import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY
from buttons.menus import get_main_menu
from db.users import update_user_economy

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")

    # פקודת 'כוח על' לאדמין
    if text == "/set_me" and user_id == str(ADMIN_ID):
        update_user_economy(user_id, slh_add=500000, xp_add=10000)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "👑 **סטטוס אדמין עודכן:**\n500,000 SLH ו-10,000 XP נוספו לארנק שלך!"})
        return

    if text == "/start":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "💎 **Diamond VIP Arcade**\nהמערכת מאובטחת ומחוברת.",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })