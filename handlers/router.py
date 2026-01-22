import requests, sqlite3, logging
from utils.config import TELEGRAM_API_URL, ADMIN_ID

# הגדרת לוגים ל-Railway
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    return sqlite3.connect('database.db')

def log_event(event):
    logging.info(f"[SYSTEM EVENT] {event}")

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # 🎰 משחקי אנימציה - עם לוגים לרילוואי
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win = 500 if (emo == "🎰" and val in [1, 22, 43, 64]) or (emo in ["🎯", "🏀", "🎳"] and val >= 5) else 0
        if win > 0:
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ?, xp = xp + 10 WHERE user_id = ?", (win, user_id))
            conn.commit(); conn.close()
            log_event(f"WIN: User {user_id} won {win} SLH on {emo}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎉 זכייה! +{win} SLH ו-+10 XP!"})
        return

    # 👑 פקודת אדמין מלאה
    if text == "/admin" and user_id == str(ADMIN_ID):
        log_event(f"ADMIN ACCESS: {user_id} opened admin panel")
        admin_msg = "🛡 **ADMIN PANEL v13**\n\nCommands: /start, /ai, /games, /profile, /help, /send\nStatus: Online & Logging"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": admin_msg})
        return

    # 🚀 ניתוב פקודות ישירות
    if text.startswith("/start"):
        ref_id = text.split(" ")[1] if len(text.split(" ")) > 1 else None
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, ref_id))
        conn.commit(); conn.close()
        log_event(f"NEW START: User {user_id}, Ref: {ref_id}")
        
        msg = "💎 **DIAMOND ELITE SUPREME**\nהאקו-סיסטם הפיננסי שלך."
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק & Mini App", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI PRO (39)", "callback_data": "ai"}, {"text": "🎰 קזינו", "callback_data": "games"}],
            [{"text": "🏆 מובילים", "callback_data": "top"}, {"text": "👥 שותפים", "callback_data": "ref"}],
            [{"text": "📈 יומן", "callback_data": "journal"}, {"text": "ℹ️ עזרה", "callback_data": "help"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif text == "/ai": handle_callback({"id":"0","from":{"id":user_id},"message":{"chat":{"id":chat_id}},"data":"ai"})
    elif text == "/games": handle_callback({"id":"0","from":{"id":user_id},"message":{"chat":{"id":chat_id}},"data":"games"})
    elif text == "/help": handle_callback({"id":"0","from":{"id":user_id},"message":{"chat":{"id":chat_id}},"data":"help"})
    
    # 🎁 מערכת העברות
    elif text.startswith("/send"):
        parts = text.split()
        if len(parts) < 3:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ פורמט: /send [כמות] [ID]"})
            return
        amount, target = int(parts[1]), parts[2]
        log_event(f"TRANSFER ATTEMPT: {user_id} to {target} amount {amount}")
        # (כאן מגיעה לוגיקת ה-DB של ההעברה שסיפקנו קודם)

    # 📝 AI ויומן
    elif text and not text.startswith("/"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן. שלח /ai לניתוח."})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "ai":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **AI PRO (39)**\nעוזר טכני צמוד + מדריך רווחים.\nלהפעלה פנה לאדמין."})
    elif data == "games":
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}, {"text": "🎯", "callback_data": "d_🎯"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
    elif data == "ref":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"👥 **שותפים:**\nhttps://t.me/OsifShop_bot?start={user_id}"})
    elif data == "help":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📜 **עזרה:** /start, /ai, /send, /games"})
    elif data.startswith("d_"):
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": data.split("_")[1]})
