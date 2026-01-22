import requests, sqlite3, logging
from utils.config import TELEGRAM_API_URL, ADMIN_ID, ADMIN_USERNAME

def get_db():
    return sqlite3.connect('database.db')

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    
    # --- פקודת MINT (אדמין בלבד) ---
    if text.startswith("/mint") and user_id == str(ADMIN_ID):
        try:
            parts = text.split()
            target_id, amount = parts[1], int(parts[2])
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
            conn.commit(); conn.close()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"✅ הונפקו {amount} SLH למשתמש {target_id}"})
        except:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ פורמט: /mint [ID] [כמות]"})
        return

    # --- תפריט ראשי עם Reply Keyboard (קבוע למטה) ---
    if text == "/start":
        msg = "💎 **DIAMOND ELITE SUPREME**\nברוך הבא למערכת הכלכלית המבוזרת שלך."
        
        # תפריט קבוע בתחתית המסך
        reply_kb = {
            "keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎰 קזינו"}], [{"text": "🤖 AI PRO"}, {"text": "ℹ️ עזרה"}]],
            "resize_keyboard": True
        }
        
        # כפתורי הודעה (Inline)
        inline_kb = {"inline_keyboard": [
            [{"text": "🚀 חזון ובלוקצ'יין", "callback_data": "roadmap"}],
            [{"text": "📞 צור קשר עם המפתח", "url": f"https://t.me/{ADMIN_USERNAME}"}],
            [{"text": "🌐 אתר הפרויקט", "url": "https://slh-nft.com/"}]
        ]}
        
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": msg, "reply_markup": reply_kb
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": "ניהול נכסים ותוכניות עתידיות:", "reply_markup": inline_kb
        })

    elif text == "💳 הארנק שלי" or text == "/profile":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "פותח ארנק...", "reply_markup": {"inline_keyboard": [[{"text": "פתח Mini App", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}]]}})

    elif text == "🎰 קזינו":
        handle_callback({"id":"0","from":{"id":user_id},"message":{"chat":{"id":chat_id}},"data":"games"})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    
    if data == "roadmap":
        msg = "🗺 **Roadmap 2026:**\n\n1️⃣ **שלב א':** מערכת נקודות פנימית (בוצע).\n2️⃣ **שלב ב':** חיבור לארנקי TON (בקרוב).\n3️⃣ **שלב ג':** מסחר ב-SLH בבורסות מבוזרות.\n\n*המערכת נבנית על תשתית בלוקצ'יין יציבה.*"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
    elif data == "games":
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
    elif data.startswith("d_"):
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": data.split("_")[1]})
