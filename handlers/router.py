import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from buttons.menus import get_main_menu
from db.users import update_user_economy

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")

    # פקודת כרייה לאדמין בלבד
    if text == "/master_mine":
        if user_id == str(ADMIN_ID):
            update_user_economy(user_id, slh_add=1000000, xp_add=10000, bal_add=5000)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": user_id, 
                "text": "👑 **ADMIN OVERRIDE**\nהוטענו 1,000,000 SLH לארנק שלך!"
            })
        else:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🚫 גישה נדחתה."})
        return

    if text == "/start":
        update_user_economy(user_id, slh_add=0)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "💎 **Diamond VIP Arcade**\nהמערכת מחוברת ומאובטחת.",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })