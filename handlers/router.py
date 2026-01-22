import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, BOT_USERNAME
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats, transfer_slh, get_leaderboard, claim_daily

user_cooldowns = {}

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")
    
    # הגנת ספאם
    now = time.time()
    if user_id in user_cooldowns and now - user_cooldowns[user_id] < 1: return
    user_cooldowns[user_id] = now

    if "dice" in message:
        val, emo = message["dice"]["value"], message["dice"]["emoji"]
        update_user_economy(user_id, xp_add=10)
        if (emo == "🏀" and val >= 4) or (emo == "🎳" and val == 6):
            update_user_economy(user_id, slh_add=70)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🔥 ביצוע מטורף! קיבלת 70 SLH!"})
        return

    if text.startswith("/start pay_"):
        target_id = text.split("_")[1]
        if transfer_slh(user_id, target_id, 50):
            msg = f"✅ שלחת 50 SLH לכתובת {target_id}!"
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": target_id, "text": "💰 קיבלת 50 SLH מחבר!"})
        else: msg = "❌ אין לך מספיק SLH."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})
        return

    if text == "/start" or text == "🔙 חזרה":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "💎 **Diamond VIP Arcade** 💎",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "בחר פעולה:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })

    elif text == "💰 הארנק שלי":
        xp, slh, bal, _ = get_user_stats(user_id)
        pay_link = f"https://t.me/{BOT_USERNAME}?start=pay_{user_id}"
        msg = f"💳 **הארנק שלך**\n\n🪙 SLH: {slh}\n✨ XP: {xp}\n💰 יתרה: {bal}\n\n🔗 לינק לתשלום:\n{pay_link}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif text == "📊 טבלת מובילים":
        top = get_leaderboard()
        msg = "🏆 **TOP 5 DIAMOND:**\n\n" + "\n".join([f"{i+1}. {u[0][:5]}... - {u[1]} SLH" for i, u in enumerate(top)])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif text == "🎁 בונוס יומי":
        if claim_daily(user_id): msg = "✅ קיבלת 50 SLH מתנה יומית!"
        else: msg = "⏳ כבר לקחת היום, חזור מחר!"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif not text.startswith("/") and OPENAI_KEY:
        # AI Logic... (GPT-4o-mini)
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "מנהל VIP כריזמטי."}, {"role": "user", "content": text}]}
        res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {OPENAI_KEY}"}).json()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": res['choices'][0]['message']['content']})
