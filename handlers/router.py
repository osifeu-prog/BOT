import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, BOT_USERNAME
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats, transfer_slh, get_leaderboard, claim_daily

user_modes = {}

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")
    now = time.time()

    # הגנת ספאם
    if user_id in user_cooldowns and now - user_cooldowns[user_id] < 1: return
    user_cooldowns[user_id] = now

    # 1. פקודת אדמין
    if text == "/admin":
        if user_id == str(ADMIN_ID):
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🛠 פאנל ניהול אדמין פעיל."})
        else:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "❌ אין לך הרשאות ניהול."})
        return

    # 2. כפתורי מערכת ו-Start
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

    # 3. הארנק המשודרג (כולל דרגות)
    if text == "💰 הארנק שלי":
        xp, slh, bal, _ = get_user_stats(user_id)
        
        if xp < 500:
            rank, next_rank = "🥉 Bronze Member", f"עוד {500-xp} XP ל-Silver"
        elif xp < 2000:
            rank, next_rank = "🥈 Silver VIP", f"עוד {2000-xp} XP ל-Diamond"
        else:
            rank, next_rank = "💎 Diamond Whale", "הגעת לדרגת המקסימום!"

        pay_link = f"https://t.me/{BOT_USERNAME}?start=pay_{user_id}"
        msg = (f"👤 **כרטיס שחקן VIP**\n━━━━━━━━━━━━\n"
               f"🏅 **דרגה:** {rank}\n"
               f"✨ **ניסיון (XP):** {xp}\n"
               f"📈 {next_rank}\n━━━━━━━━━━━━\n"
               f"🪙 **מטבעות SLH:** {slh}\n"
               f"💰 **יתרה למימוש:** {bal}\n\n"
               f"🔗 **לינק אישי:**\n{pay_link}")
        
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": [[{"text": "💳 בקשת משיכה", "callback_data": "withdraw_req"}]]}
        })
        return

    # 4. מצב AI
    if text == "🤖 שאל את ה-AI":
        user_modes[user_id] = "ai"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🤖 **מצב AI פעיל.**\nשאל אותי הכל על המערכת או שוק הון.\nלחץ 'חזרה' כדי לצאת.",
            "reply_markup": {"keyboard": [[{"text": "🔙 חזרה"}]], "resize_keyboard": True}
        })
        return

    # 5. מענה AI
    if user_modes.get(user_id) == "ai" and not text.startswith("/"):
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "אתה מנהל VIP כריזמטי."}, {"role": "user", "content": text}]}
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {OPENAI_KEY}"})
            res = r.json()
            reply = res['choices'][0]['message']['content'] if 'choices' in res else "⚠️ שגיאת AI."
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": reply})
        except:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "❌ שגיאה בחיבור."})
        return

user_cooldowns = {}