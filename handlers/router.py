import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, ADMIN_USERNAME
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats

async def handle_message(message):
    user_id = str(message["from"]["id"])
    
    # 1. זיהוי משחקים (Dice)
    if "dice" in message:
        val = message["dice"]["value"]
        emoji = message["dice"]["emoji"]
        update_user_economy(user_id, xp_add=10) # 10 XP על השתתפות
        if (emoji == "🏀" and val >= 4) or (emoji == "🎳" and val == 6) or (emoji == "🎯" and val == 6):
            update_user_economy(user_id, slh_add=50)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🔥 הצלחה! זכית ב-50 SLH!"})
        return

    text = message.get("text", "")

    # 2. פקודת אדמין
    if text == "/admin" and user_id == ADMIN_ID:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🛠 **פאנל ניהול אדמין**\nהמערכת יציבה.",
            "reply_markup": {"inline_keyboard": [[{"text": "📢 הודעת תפוצה", "callback_data": "admin_broadcast"}]]}
        })
        return

    # 3. ניווט ותפריטים
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
        msg = f"💳 **הארנק שלך**\n\n🪙 SLH: {slh}\n✨ XP: {xp}\n💰 יתרה: {bal}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif text == "🎮 משחקים ופרסים":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 בחר משחק:", "reply_markup": {"inline_keyboard": get_games_menu()}
        })

    # 4. מענה AI (רק אם זה לא פקודה)
    elif not text.startswith("/") and text not in ["💰 הארנק שלי", "🎮 משחקים ופרסים"] and OPENAI_KEY:
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        ai_url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "Expert crypto/stock mentor. Hebrew."}, {"role": "user", "content": text}]
        }
        try:
            res = requests.post(ai_url, json=payload, headers=headers).json()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": res['choices'][0]['message']['content']})
        except:
            pass
