import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import add_xp, get_user_data

async def handle_message(message):
    user_id = message["from"]["id"]
    
    # בדיקה אם ההודעה היא תוצאה של משחק (Dice)
    if "dice" in message:
        value = message["dice"]["value"]
        emoji = message["dice"]["emoji"]
        xp_won = 0
        msg = ""

        if emoji == "🏀" and value >= 4:
            xp_won = 50
            msg = "🏀 סל מטורף! זכית ב-50 XP!"
        elif emoji == "🎳" and value == 6:
            xp_won = 100
            msg = "🎳 סטרייק!! זכית ב-100 XP!"
        elif emoji == "🎯" and value == 6:
            xp_won = 150
            msg = "🎯 בול פגיעה! זכית ב-150 XP!"
        
        if xp_won > 0:
            add_xp(user_id, xp_won)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})
        return

    text = message.get("text", "")
    if text == "/start" or text == "🔙 חזרה":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "🏆 **Diamond Arcade VIP**\nהארנק שלך פעיל!",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "בחר אפשרות:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })

    elif text == "💰 הארנק שלי":
        xp, bal, refs = get_user_data(user_id)
        level = "טירון" if xp < 500 else "סוחר מתקדמת" if xp < 2000 else "לווייתן VIP"
        msg = f"💳 **הארנק שלך**\n\n✨ נקודות (XP): {xp}\n🏆 דרגה: {level}\n💰 יתרה: {bal}\n👥 חברים שהזמנת: {refs}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif text == "🎮 משחקים ופרסים":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 בחר משחק:", "reply_markup": {"inline_keyboard": get_games_menu()}
        })
