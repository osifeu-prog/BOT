import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, BOT_USERNAME
from buttons.menus import get_main_menu
from db.users import update_user_economy, get_user_stats, transfer_slh

user_modes = {}

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")

    # --- פקודת כרייה סודית לאדמין בלבד ---
    if text == "/mine":
        if user_id == str(ADMIN_ID):
            update_user_economy(user_id, slh_add=1000000, xp_add=5000)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "💎 **ADMIN MINING COMPLETE**\nנוספו 1,000,000 SLH ו-5,000 XP לארנק המאסטר שלך."})
        else:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "❌ גישה נדחתה. אתה לא המנהל."})
        return

    # --- מניעת זיופים בהעברות ---
    if text.startswith("/pay"):
        try:
            parts = text.split()
            target_id, amount = parts[1], int(parts[2])
            if amount <= 0: raise ValueError("Amount must be positive")
            
            # בדיקה שהשולח לא שולח לעצמו (מניעת לופ XP)
            if user_id == target_id:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🚫 אי אפשר להעביר לעצמך!"})
                return

            if transfer_slh(user_id, target_id, amount):
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": f"✅ העברת {amount} SLH בהצלחה."})
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": target_id, "text": f"💰 קיבלת {amount} SLH מיוזר {user_id}!"})
            else:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "❌ יתרה נמוכה מדי."})
        except:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "⚠️ פורמט: /pay ID AMOUNT"})
        return

    # חזרה לתפריט ראשי
    if text == "/start" or text == "🔙 חזרה לתפריט":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "💎 **Diamond VIP**\nמערכת מאובטחת ומשופרת.",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })