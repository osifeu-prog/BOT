import requests, sqlite3
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def get_db():
    return sqlite3.connect('database.db')

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # 🎰 טיפול במשחקי אנימציה
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win = 500 if (emo == "🎰" and val in [1, 22, 43, 64]) or (emo in ["🎯", "🏀", "🎳"] and val >= 5) else 0
        if win > 0:
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win, user_id))
            conn.commit(); conn.close()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🔥 פגיעה בול! זכית ב-{win} SLH!"})
        return

    # 👑 פקודת אדמין וניהול מערכת
    if text == "/admin" and user_id == str(ADMIN_ID):
        admin_msg = (
            "🛡 **פאנל ניהול - Diamond Elite**\n\n"
            "📊 **סטטוס פרויקט:** Alpha v12.0 - Active\n"
            "📜 **פקודות בוט:**\n"
            "• /start - תפריט ראשי\n"
            "• /profile - כרטיס משתמש\n"
            "• /games - קזינו ומשחקים\n"
            "• /ai - עוזר חכם\n"
            "• /wallet - פתיחת המיני-אפ\n\n"
            "🚀 **מה בוצע:** חיבור DB, משחקי אנימציה, יומן, שותפים.\n"
            "🛠 **להמשך:** אוטומציה של אישור תשלום, התראות מחיר בזמן אמת, עיצוב מחדש למיני-אפ."
        )
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": admin_msg, "parse_mode": "Markdown"})
        return

    # 🚀 פקודות ישירות
    if text == "/start":
        msg = "💎 **DIAMOND ELITE SUPREME**\nהעוזר הפיננסי המלא שלך מוכן."
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק & Mini App", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI PRO (מדריך ב-39)", "callback_data": "ai_pro"}, {"text": "📈 יומן שוק", "callback_data": "journal"}],
            [{"text": "🎰 משחקים", "callback_data": "games"}, {"text": "🏆 מובילים", "callback_data": "top"}],
            [{"text": "👥 שותפים", "callback_data": "ref"}, {"text": "📞 ערוץ VIP", "callback_data": "vip_link"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})
    
    elif text in ["/ai", "/games", "/profile", "/wallet"]:
        handle_callback({"id": "0", "from": {"id": user_id}, "message": {"chat": {"id": chat_id}}, "data": text[1:]})

    # 📝 שמירה ליומן ו-AI
    elif text and not text.startswith("/"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **AI Insight:** נרשם ביומן. שלח /ai לניתוח מעמיק."})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "ai_pro" or data == "ai":
        msg = "🎓 **AI PRO - עוזר כלכלי אישי**\nב-39 בלבד: מדריך רווחים, ניתוח תיק השקעות, וגישה חופשית.\n\n[לינק לתשלום/פנייה לאדמין]"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
    elif data == "games":
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}, {"text": "🎯", "callback_data": "d_🎯"}, {"text": "🎳", "callback_data": "d_🎳"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
    elif data == "ref":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"👥 **תוכנית שותפים:**\nשלח את הלינק: 	.me/OsifShop_bot?start={user_id}\nבונוס: 500 SLH לכל חבר!", "parse_mode": "Markdown"})
    elif data == "vip_link":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🔓 **קבוצת VIP:** הלינק ייפתח אוטומטית לאחר רכישת AI PRO."})
    elif data == "top":
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        res = "\n".join([f"👤 {r[0]}: {r[1]} SLH" for r in c.fetchall()])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🏆 **מובילים:**\n{res}"})
    elif data.startswith("d_"):
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": data.split("_")[1]})
