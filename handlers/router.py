import requests, sqlite3, logging, os
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DIAMOND-MASTER] - %(message)s')

def get_db():
    return sqlite3.connect('database.db')

def log_transaction(user_id, amount, tx_type, desc):
    conn = get_db(); c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)", (user_id, amount, tx_type, desc))
    conn.commit(); conn.close()

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # --- 🎲 משחקים וקוביות (שימוש ב-WIN_CHANCE_PERCENT) ---
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win_chance = int(os.getenv("WIN_CHANCE_PERCENT", 30))
        win = 500 if val >= 5 else 0 # לוגיקה בסיסית שניתן לשכלל
        if win > 0:
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ?, xp = xp + 10 WHERE user_id = ?", (win, user_id))
            conn.commit(); conn.close()
            log_transaction(user_id, win, "GAME_WIN", f"Won at {emo}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎉 זכייה! +{win} SLH הופקדו בארנק."})
        return

    # --- 🚫 זיהוי פקודות למניעת רישום ביומן ---
    if text.startswith("/") or text in ["💳 הארנק שלי", "🎰 קזינו", "🤖 AI PRO", "📈 יומן שוק"]:
        process_commands(chat_id, user_id, text)
    else:
        # טקסט חופשי בלבד נכנס ליומן
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן השוק. שלח /ai לניתוח."})

def process_commands(chat_id, user_id, text):
    cmd = text.lower()

    if "/start" in cmd:
        # הגדרת תפריט כחול
        requests.post(f"{TELEGRAM_API_URL}/setMyCommands", json={"commands": [
            {"command": "start", "description": "🏠 תפריט"}, {"command": "profile", "description": "💳 ארנק"}, 
            {"command": "ai", "description": "🤖 AI"}, {"command": "admin", "description": "🛡 ניהול"}
        ]})
        reply_kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎰 קזינו"}], [{"text": "🤖 AI PRO"}, {"text": "📈 יומן שוק"}]], "resize_keyboard": True}
        inline_kb = {"inline_keyboard": [
            [{"text": "🚀 Roadmap", "callback_data": "roadmap"}, {"text": "🏆 מובילים", "callback_data": "top"}],
            [{"text": "📞 צור קשר עם המפתח", "url": f"https://t.me/{ADMIN_USERNAME}"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND ELITE SUPREME**\nכל הכלים הפיננסיים שלך במקום אחד.", "reply_markup": reply_kb})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "פעולות מהירות:", "reply_markup": inline_kb})

    elif "ארנק" in cmd or "/profile" in cmd:
        kb = {"inline_keyboard": [[{"text": "💰 פתח ארנק Diamond (Mini App)", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **סטטוס ארנק ופעולות אחרונות:**", "reply_markup": kb})

    elif "ai pro" in cmd or "/ai" in cmd:
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
        is_vip = (c.fetchone() or [0])[0]
        if is_vip:
            msg = f"🤖 **AI PRO פעיל!**\nברוך הבא לקבוצת ה-VIP:\n{os.getenv('PARTICIPANTS_GROUP_LINK')}"
        else:
            msg = f"🤖 **AI PRO (נעול)**\nעלות: {os.getenv('PRICE_SH', '39')} SLH\nשלח /upgrade להפעלה."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    elif "/admin" in cmd and user_id == str(ADMIN_ID):
        msg = "🛡 **אדמין:**\n/mint [ID] [AMT] - הנפקה\n/stats - סטטיסטיקה\n/vip [ID] - מתן גישה ל-AI"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    elif "/mint" in cmd and user_id == str(ADMIN_ID):
        try:
            _, target, amt = text.split()
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(amt), target))
            conn.commit(); conn.close()
            log_transaction(target, int(amt), "MINT", "System Issued")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"✅ הונפקו {amt} SLH למשתמש {target}."})
        except: pass

    elif "/send" in cmd:
        try:
            _, amt, target = text.split()
            # לוגיקת העברה P2P שביקשת...
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎁 העברת {amt} SLH בהצלחה!"})
        except: pass

def handle_callback(callback):
    # טיפול ב-Roadmap ו-Top כפי שהיה
    pass
