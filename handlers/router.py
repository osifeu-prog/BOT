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

    if user_id in user_cooldowns and now - user_cooldowns[user_id] < 0.5: return
    user_cooldowns[user_id] = now

    # פקודות בסיס
    if text == "/start" or text == "🔙 חזרה לתפריט":
        user_modes[user_id] = None
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "💎 **Diamond VIP Arcade**\nברוך הבא לסטנדרט החדש של שוק ההון.",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "בחר את הפעולה המבוקשת:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
        return

    if text == "💰 הארנק שלי":
        xp, slh, bal, _ = get_user_stats(user_id)
        rank = "🥉 Bronze" if xp < 500 else "🥈 Silver VIP" if xp < 2000 else "💎 Diamond Whale"
        msg = (f"👤 **כרטיס חבר VIP**\n━━━━━━━━━━━━\n"
               f"🏅 **סטטוס:** {rank}\n"
               f"✨ **XP:** {xp}\n━━━━━━━━━━━━\n"
               f"🪙 **SLH:** {slh}\n"
               f"💰 **יתרה בארנק:** {bal}\n\n"
               f"🔗 **לינק אישי להעברות:**\nhttps://t.me/{BOT_USERNAME}?start=pay_{user_id}")
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": [[{"text": "📊 היסטוריית פעולות", "callback_data": "history"}]]}})
        return

    if text == "🤖 שאל את ה-AI":
        user_modes[user_id] = "ai"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🤖 **מצב אנליסט VIP פעיל**\nאני זמין לשאלות על שוק הון, קריפטו או שימוש בבוט.\nלחץ על הכפתור למטה כדי לחזור.",
            "reply_markup": {"keyboard": [[{"text": "🔙 חזרה לתפריט"}]], "resize_keyboard": True}
        })
        return

    # לוגיקת AI מתקדמת
    if user_modes.get(user_id) == "ai" and not text.startswith("/"):
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        system_msg = "אתה אנליסט בכיר במועדון Diamond VIP. תפקידך לתת עצות פיננסיות (עם דיסקליימר) ולעודד שימוש בבוט: משחקים, צבירת SLH וקורסים."
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": text}]}
        r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {OPENAI_KEY}"}).json()
        reply = r['choices'][0]['message']['content'] if 'choices' in r else "⚠️ האנליסט עסוק, נסה שוב."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": reply})
        return

    if text == "/admin" and user_id == str(ADMIN_ID):
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🕶 **Welcome Master.**\nכל המערכות פועלות כשורה."})