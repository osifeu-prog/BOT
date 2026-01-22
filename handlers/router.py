import requests, sqlite3, logging, os
from utils.config import *

logging.basicConfig(level=logging.INFO)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = os.getenv('ADMIN_ID')

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    
    if not text: return

    # --- 1. מנגנון START / מתנות / אפילייט ---
    if text.startswith("/start"):
        args = text.split()
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        
        if not user:
            # רישום משתמש חדש
            c.execute("INSERT INTO users (user_id, balance, xp, rank) VALUES (?, 0, 0, 'Starter')", (user_id,))
            conn.commit()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ADMIN_ID, "text": f"👤 משתמש חדש: {user_id}"})
            
            # בדיקת רפרל/מתנה רק למשתמש חדש
            if len(args) > 1:
                ref_data = args[1]
                if ref_data.startswith("gift_"):
                    c.execute("UPDATE users SET balance = balance + 500 WHERE user_id = ?", (user_id,))
                    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎁 קיבלת מתנה של 500 SLH!"})
                elif ref_data != user_id:
                    reward = int(os.getenv("REFERRAL_REWARD", 500))
                    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, ref_data))
                    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ref_data, "text": f"👥 חבר הצטרף! קיבלת {reward} SLH."})
        
        conn.commit(); conn.close()
        send_menu(chat_id)

    # --- 2. מניעת רישום פקודות ביומן ---
    elif text in ["💳 הארנק שלי", "🎁 בונוס יומי", "🎰 קזינו", "🤖 ניתוח יומן"]:
        if text == "💳 הארנק שלי":
            kb = {"inline_keyboard": [[{"text": "💰 פתח ארנק מלא", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}]]}
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **סטטוס ארנק:**", "reply_markup": kb})
        elif text == "🎁 בונוס יומי":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ אספת 100 SLH (זמני - נדרש בדיקת 24ש')."})
        # ... שאר הכפתורים

    # --- 3. יומן שוק (טקסט חופשי בלבד) ---
    else:
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן השוק."})

def send_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], [{"text": "🎰 קזינו"}, {"text": "🤖 ניתוח יומן"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND SUPREME**\nהמערכת מוכנה.", "reply_markup": kb})
