import requests, sqlite3, logging
from utils.config import TELEGRAM_API_URL, ADMIN_ID

# לוגים של המערכת ל-Railway
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DIAMOND-LOG] - %(message)s')

def get_db():
    return sqlite3.connect('database.db')

def log_tx(user_id, amount, tx_type, desc):
    conn = get_db(); c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)", (user_id, amount, tx_type, desc))
    conn.commit(); conn.close()
    logging.info(f"TX: {user_id} | {tx_type} | {amount} | {desc}")

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # --- משחקים עם XP וזכיות ---
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win = 500 if (emo == "🎰" and val in [1, 22, 43, 64]) or (emo in ["🎯", "🏀", "🎳"] and val >= 5) else 0
        conn = get_db(); c = conn.cursor()
        c.execute("UPDATE users SET xp = xp + 5 WHERE user_id = ?", (user_id,))
        if win > 0:
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win, user_id))
            log_tx(user_id, win, "GAME_WIN", f"Won at {emo}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎊 בול! זכית ב-{win} SLH וצברת 5 XP!"})
        conn.commit(); conn.close()
        return

    # --- ניתוב פקודות ישירות (לא נעלמות לעולם) ---
    cmd = text.split()[0].lower() if text.startswith("/") else None
    
    if cmd == "/start":
        ref_id = text.split()[1] if len(text.split()) > 1 else None
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, ref_id))
        conn.commit(); conn.close()
        
        msg = "💎 **DIAMOND ELITE SUPREME**\nהאקו-סיסטם הפיננסי שלך מוכן לפעולה.\n\nבחר מהתפריט למטה או השתמש בפקודות המהירות."
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק & Mini App", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI PRO (39)", "callback_data": "ai_pro"}, {"text": "🎰 קזינו", "callback_data": "games_menu"}],
            [{"text": "📊 מובילים", "callback_data": "top_players"}, {"text": "📈 יומן שוק", "callback_data": "journal_view"}],
            [{"text": "👥 שותפים", "callback_data": "share_link"}, {"text": "ℹ️ מדריך עזרה", "callback_data": "help_guide"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif cmd == "/admin" and user_id == str(ADMIN_ID):
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🛡 **פאנל ניהול:**\n- לוגים פעילים ב-Railway\n- מערכת העברות: פעילה\n- סטטוס: v14.0 Stable"})

    elif cmd == "/send":
        parts = text.split()
        if len(parts) < 3:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ פורמט: /send [כמות] [ID]"})
            return
        amount, target = int(parts[1]), parts[2]
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        if (c.fetchone() or [0])[0] >= amount:
            c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target))
            conn.commit(); conn.close()
            log_tx(user_id, -amount, "GIFT", f"To {target}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎁 שלחת {amount} SLH כמתנה!"})
        else: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ אין מספיק SLH."})

    elif cmd in ["/ai", "/games", "/help", "/profile"]:
        handle_callback({"id":"0","from":{"id":user_id},"message":{"chat":{"id":chat_id}},"data":cmd[1:]})

    # --- AI יומן ותובנות ---
    elif text and not text.startswith("/"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן. שלח /ai לניתוח הנתונים."})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if "ai" in data:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **AI PRO (39):**\nעוזר טכני, מדריך רווחים ויועץ שוק אישי.\nפנה לאדמין להפעלה מיידית."})
    elif "games" in data:
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}, {"text": "🎳", "callback_data": "d_🎳"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
    elif "share" in data or "ref" in data:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"👥 **לינק שותפים (500 SLH):**\nhttps://t.me/OsifShop_bot?start={user_id}"})
    elif "help" in data:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📜 **פקודות:**\n/start - תפריט\n/send [כמות] [ID] - מתנה\n/ai - עוזר\n/profile - ארנק"})
    elif data.startswith("d_"):
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": data.split("_")[1]})
