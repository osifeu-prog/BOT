import requests, sqlite3, logging
from utils.config import TELEGRAM_API_URL, ADMIN_ID, ADMIN_USERNAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CORE] - %(message)s')

def get_db():
    return sqlite3.connect('database.db')

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # --- 1. מנוע פקודות אדמין (MINT) ---
    if text.startswith("/mint") and user_id == str(ADMIN_ID):
        try:
            _, target, amt = text.split()
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(amt), target))
            conn.commit(); conn.close()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"💎 הונפקו {amt} SLH למשתמש {target}. המערכת מתרחבת!"})
        except: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ שימוש: /mint [ID] [כמות]"})
        return

    # --- 2. תפריט פקודות (Bot Menu Button) ---
    # נשלח פעם אחת ב-Start כדי להגדיר את הכפתור ליד המקלדת
    if text == "/start":
        requests.post(f"{TELEGRAM_API_URL}/setMyCommands", json={"commands": [
            {"command": "start", "description": "תפריט ראשי"},
            {"command": "profile", "description": "הארנק שלי"},
            {"command": "ai", "description": "AI PRO"},
            {"command": "help", "description": "עזרה ותמיכה"}
        ]})
        
        # תפריט מקלדת (Reply)
        reply_kb = {
            "keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎰 קזינו"}], [{"text": "🤖 AI PRO"}, {"text": "📈 יומן שוק"}]],
            "resize_keyboard": True
        }
        
        # כפתורי הודעה (Inline)
        inline_kb = {"inline_keyboard": [
            [{"text": "🚀 חזון ובלוקצ'יין", "callback_data": "roadmap"}, {"text": "🏆 מובילים", "callback_data": "top"}],
            [{"text": "📞 צור קשר עם המפתח", "url": f"https://t.me/{ADMIN_USERNAME}"}],
            [{"text": "🌐 אתר SLH-NFT", "url": "https://slh-nft.com/"}]
        ]}
        
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, 
            "text": "💎 **DIAMOND ELITE SUPREME**\nהארנק הדיגיטלי והעוזר האישי שלך.\n\nהשתמש במקלדת למטה לגישה מהירה.",
            "reply_markup": reply_kb,
            "parse_mode": "Markdown"
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": "פעולות נוספות:", "reply_markup": inline_kb
        })

    # --- 3. ניתוב כפתורי מקלדת ---
    elif text == "💳 הארנק שלי":
        kb = {"inline_keyboard": [[{"text": "פתח ארנק מלא (Mini App)", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **סטטוס ארנק:**\nהמערכת מוכנה לחיבור לרשת TON.\nצפה בנכסים שלך:", "reply_markup": kb})
    
    elif text == "🤖 AI PRO":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **AI PRO (39)**\nעוזר טכני צמוד, מדריך רווחים וניתוח שוק.\n\n*המערכת שומרת את התובנות שלך ביומן.*"})

    elif text == "📈 יומן שוק":
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT entry FROM user_journal WHERE user_id = ? ORDER BY id DESC LIMIT 3", (user_id,))
        entries = "\n".join([f"• {r[0]}" for r in c.fetchall()])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📝 **תובנות אחרונות:**\n{entries or 'היומן ריק.'}"})

    # --- 4. טיפול בטקסט חופשי (יומן) ---
    elif text and not text.startswith("/"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נשמר ביומן. ה-AI מנתח את המידע..."})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "roadmap":
        msg = "🗺 **Roadmap 2026:**\n\n1️⃣ **Minting:** הנפקת SLH (פעיל).\n2️⃣ **Web3:** חיבור לארנקי TON (בפיתוח).\n3️⃣ **Elite:** מסחר מבוזר מלא."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
    elif data == "top":
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        res = "\n".join([f"👤 {r[0]}: {r[1]} SLH" for r in c.fetchall()])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🏆 **מובילים:**\n{res}"})
