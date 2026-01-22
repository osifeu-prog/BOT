import requests, sqlite3
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def get_db():
    return sqlite3.connect('database.db')

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # 🎰 טיפול במשחקי אנימציה ועדכון כסף אמיתי
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win = 0
        if emo == "🎰" and val in [1, 22, 43, 64]: win = 777
        elif emo in ["🎯", "🏀", "🎳"] and val >= 5: win = 250
        
        if win > 0:
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win, user_id))
            conn.commit(); conn.close()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🔥 זכייה! +{win} SLH התווספו לארנק!"})
        return

    # 🚀 תפריט התחלה ומערכת שותפים
    if text.startswith("/start"):
        ref_id = text.split(" ")[1] if len(text.split(" ")) > 1 else None
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, ref_id))
        if ref_id and ref_id != user_id:
             c.execute("UPDATE users SET balance = balance + 500 WHERE user_id = ?", (ref_id,))
        conn.commit(); conn.close()

        msg = "💎 **DIAMOND ELITE SUPREME**\nהעוזר הפיננסי המלא שלך מוכן."
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק & Mini App", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI PRO (מדריך ב-39)", "callback_data": "ai_pro"}, {"text": "📈 יומן שוק אישי", "callback_data": "journal"}],
            [{"text": "🎰 מתחם משחקים", "callback_data": "games"}, {"text": "🏆 מובילים", "callback_data": "top"}],
            [{"text": "🌐 אתר SLH-NFT", "url": "https://slh-nft.com/"}, {"text": "👥 שותפים", "callback_data": "ref"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    # 📝 שמירה ליומן (כל טקסט אחר)
    elif text and not text.startswith("/"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן השוק שלך."})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "ai_pro":
        msg = "🎓 **מסלול AI PRO (39)**\nעוזר טכני לא מוגבל + מדריך רווחים.\nלהפעלה פנה לאדמין."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
    elif data == "games":
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}, {"text": "🎯", "callback_data": "d_🎯"}, {"text": "🎳", "callback_data": "d_🎳"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
    elif data.startswith("d_"):
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": data.split("_")[1]})
    elif data == "top":
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        res = "\n".join([f"👤 {r[0]}: {r[1]} SLH" for r in c.fetchall()])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🏆 **מובילים:**\n{res}"})
    elif data == "journal":
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT entry FROM user_journal WHERE user_id = ? ORDER BY id DESC LIMIT 3", (user_id,))
        res = "\n".join([f"• {r[0]}" for r in c.fetchall()])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📝 **תובנות אחרונות:**\n{res or 'היומן ריק.'}"})
