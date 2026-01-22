import requests
from utils.config import TELEGRAM_API_URL, OPENAI_KEY
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats

async def handle_message(message):
    user_id = message["from"]["id"]
    
    # לוגיקת זכייה במשחקים
    if "dice" in message:
        val = message["dice"]["value"]
        emoji = message["dice"]["emoji"]
        xp, slh = 10, 0 # כל משחק נותן 10 XP על השתתפות
        msg = ""

        if (emoji == "🏀" and val >= 4) or (emoji == "🎳" and val == 6) or (emoji == "🎯" and val == 6):
            slh = 50
            msg = f"🔥 מדהים! הצלחת וזכית ב-50 מטבעות SLH!"
        
        update_user_economy(user_id, xp, slh)
        if msg: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})
        return

    text = message.get("text", "")
    if text == "/start" or text == "🔙 חזרה":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🏆 **Diamond Arcade VIP**",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "בחר פעולה:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })

    elif text == "💰 הארנק שלי":
        xp, slh, bal = get_user_stats(user_id)
        msg = f"💳 **הארנק שלך**\n\n🪙 מטבעות SLH: {slh}\n✨ נקודות XP: {xp}\n💰 יתרה: {bal}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})
