import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, BOT_USERNAME
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats, transfer_slh, get_leaderboard, claim_daily

user_modes = {}
user_cooldowns = {}

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")
    now = time.time()

    if user_id in user_cooldowns and now - user_cooldowns[user_id] < 0.8: return
    user_cooldowns[user_id] = now

    if text == "/admin":
        if user_id == str(ADMIN_ID):
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🛠 פאנל ניהול אדמין פעיל."})
        return

    if text == "/start" or text == "🔙 חזרה":
        user_modes[user_id] = None
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "💎 **Diamond VIP Arcade**\nברוך הבא למערכת המשופרת!",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "בחר פעולה:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
        return

    if text == "💰 הארנק שלי":
        xp, slh, bal, _ = get_user_stats(user_id)
        rank = "🥉 Bronze Member" if xp < 500 else "🥈 Silver VIP" if xp < 2000 else "💎 Diamond Whale"
        pay_link = f"https://t.me/{BOT_USERNAME}?start=pay_{user_id}"
        msg = (f"👤 **כרטיס שחקן VIP**\n━━━━━━━━━━━━\n"
               f"🏅 **דרגה:** {rank}\n"
               f"✨ **ניסיון:** {xp}\n━━━━━━━━━━━━\n"
               f"🪙 **SLH:** {slh}\n"
               f"💰 **יתרה:** {bal}\n\n"
               f"🔗 **לינק אישי:**\n{pay_link}")
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})
        return

    # הפעלת AI דרך טקסט או כפתור
    if "AI" in text or text == "🤖 שאל את ה-AI":
        user_modes[user_id] = "ai"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🤖 מצב AI פעיל. אני מקשיב..."})
        return

    # לוגיקת AI
    if user_modes.get(user_id) == "ai" and not text.startswith("/"):
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "אתה מנהל VIP. תמליץ על משחקים, קורסים וצבירת SLH."}, {"role": "user", "content": text}]}
        r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {OPENAI_KEY}"}).json()
        reply = r['choices'][0]['message']['content'] if 'choices' in r else "⚠️ ה-AI נח כרגע."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": reply})
        return