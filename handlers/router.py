import requests, sqlite3
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def get_db():
    return sqlite3.connect('database.db')

def log_tx(user_id, amount, tx_type, desc):
    conn = get_db(); c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)", (user_id, amount, tx_type, desc))
    conn.commit(); conn.close()

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # 🎁 מערכת העברות ומתנות (/send amount user_id)
    if text.startswith("/send"):
        parts = text.split()
        if len(parts) < 3:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ פורמט: /send [כמות] [ID_משתמש]"})
            return
        amount, target_id = int(parts[1]), parts[2]
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        bal = c.fetchone()[0]
        if bal >= amount:
            c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
            conn.commit(); conn.close()
            log_tx(user_id, -amount, "Transfer", f"Sent to {target_id}")
            log_tx(target_id, amount, "Transfer", f"Received from {user_id}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"✅ שלחת {amount} SLH בהצלחה!"})
        else:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ יתרה לא מספקת."})
        return

    # 🎰 משחקים עם תיעוד היסטוריה
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win = 500 if (emo == "🎰" and val in [1, 22, 43, 64]) or (emo in ["🎯", "🏀", "🎳"] and val >= 5) else 0
        if win > 0:
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ?, xp = xp + 10 WHERE user_id = ?", (win, user_id))
            conn.commit(); conn.close()
            log_tx(user_id, win, "Game Win", f"Won at {emo}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎉 זכייה! +{win} SLH ו-+10 XP!"})
        return

    # 🚀 פקודות ראשיות
    if text == "/start":
        msg = "💎 **DIAMOND ELITE SUPREME**\nהאקו-סיסטם הפיננסי שלך."
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק & היסטוריה", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI PRO (39)", "callback_data": "ai_pro"}, {"text": "📈 יומן שוק", "callback_data": "journal"}],
            [{"text": "🎰 קזינו", "callback_data": "games"}, {"text": "🏆 מובילים", "callback_data": "top"}],
            [{"text": "👥 שותפים", "callback_data": "ref"}, {"text": "ℹ️ עזרה", "callback_data": "help"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "help":
        msg = "📜 **מדריך פקודות:**\n/start - תפריט\n/send [כמות] [ID] - שליחת כסף\n/ai - עוזר חכם\n/admin - ניהול (לאדמין)"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
    elif data == "games":
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}, {"text": "🎯", "callback_data": "d_🎯"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
    elif data.startswith("d_"):
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": data.split("_")[1]})
    elif data == "ref":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"👥 **לינק שותפים:**\n	.me/OsifShop_bot?start={user_id}"})
