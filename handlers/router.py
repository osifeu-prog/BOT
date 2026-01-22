import requests, sqlite3, logging, os
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data")
    if data == "dep":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📥 **הפקדה ידנית:**\nשלח TON לכתובת:\n{os.getenv('TON_WALLET', 'Contact Admin')}\nושלח צילום מסך לאדמין.", "parse_mode": "Markdown"})

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    if not text: return

    # --- פקודות אדמין (Admin Only) ---
    if user_id == ADMIN_ID:
        if text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "")
            conn = get_db(); users = conn.execute("SELECT user_id FROM users").fetchall()
            for u in users:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": u['user_id'], "text": f"📢 **הודעה מהמערכת:**\n{msg}"})
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ ההודעה נשלחה לכולם."})
            return
        
        elif text.startswith("/mint "): # פורמט: /mint [ID] [AMOUNT]
            _, target, amt = text.split()
            conn = get_db(); conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amt, target))
            conn.commit(); conn.close()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"✅ הופקדו {amt} SLH למשתמש {target}"})
            return

        elif text == "/stats":
            conn = get_db(); count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📊 **סטטיסטיקה:**\nמשתמשים רשומים: {count}"})
            return

    # --- פקודות משתמש רגילות ---
    if text.startswith("/start"):
        conn = get_db(); c = conn.cursor()
        user = c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user:
            c.execute("INSERT INTO users (user_id, balance, xp, rank) VALUES (?, 0, 0, 'Starter')", (user_id,))
            conn.commit()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ADMIN_ID, "text": f"🆕 משתמש חדש: {user_id}"})
        conn.close()
        send_menu(chat_id)

    elif text == "💳 הארנק שלי":
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        msg = f"📊 **החשבון שלי**\n💰 יתרה: {user['balance']} SLH\n🏆 XP: {user['xp']}\n🏅 דרגה: {user['rank']}"
        kb = {"inline_keyboard": [[{"text": "💰 פתח מיני-אפ", "web_app": {"url": f"https://{os.getenv('RAILWAY_STATIC_URL')}/"}}, {"text": "📥 הפקדה", "callback_data": "dep"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    elif text == "🤖 ניתוח יומן":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🧠 ה-AI מנתח את הפעילות שלך... (פונקציה זו דורשת OpenAI Key)"})

    else:
        # רישום ביומן
        conn = get_db(); conn.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📝 נרשם ביומן השוק."})

def send_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], [{"text": "🎰 קזינו"}, {"text": "🤖 ניתוח יומן"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND SUPREME SYSTEM**\nכל המערכות פעילות. השתמש בתפריט למטה:", "reply_markup": kb})
