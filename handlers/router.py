import requests, sqlite3, logging, os, datetime
from utils.config import *

logging.basicConfig(level=logging.INFO)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = os.getenv('ADMIN_ID')

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- פונקציית התיקון שחסרה בלוגים שלך ---
def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data")
    if data == "dep":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📥 להפקדה, שלח TON לכתובת:\n{os.getenv('TON_WALLET', 'Contact Admin')}", "parse_mode": "Markdown"})

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    if not text: return

    # --- 1. מנגנון האפילייטס והמתנות המלא ---
    if text.startswith("/start"):
        args = text.split()
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (user_id, balance, xp, rank) VALUES (?, 0, 0, 'Starter')", (user_id,))
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ADMIN_ID, "text": f"👤 משתמש חדש: {user_id}"})
            
            if len(args) > 1:
                ref = args[1]
                if ref.startswith("gift_"):
                    c.execute("UPDATE users SET balance = balance + 500 WHERE user_id = ?", (user_id,))
                    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎁 מתנת הצטרפות של 500 SLH הופקדה!"})
                elif ref != user_id:
                    reward = int(os.getenv("REFERRAL_REWARD", 500))
                    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, ref))
                    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ref, "text": "👥 חבר נרשם! קיבלת בונוס שותפים."})
        conn.commit(); conn.close()
        send_main_menu(chat_id)

    # --- 2. מניעת כתיבת פקודות ביומן (ניקיון המערכת) ---
    elif text in ["💳 הארנק שלי", "🎁 בונוס יומי", "🎰 קזינו", "🤖 ניתוח יומן"]:
        process_button(chat_id, user_id, text)

    # --- 3. יומן שוק נקי (רק טקסט חופשי נכנס לכאן) ---
    else:
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן השוק."})

def process_button(chat_id, user_id, text):
    if text == "💳 הארנק שלי":
        kb = {"inline_keyboard": [[{"text": "💰 פתח ארנק מלא", "web_app": {"url": f"https://{os.getenv('RAILWAY_STATIC_URL')}/"}}, {"text": "📥 הפקדה", "callback_data": "dep"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **ניהול נכסים:**", "reply_markup": kb})
    elif text == "🎁 בונוס יומי":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎁 קיבלת 100 SLH! (בונוס יומי מוכן)"})
    elif text == "🤖 ניתוח יומן":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🧠 ה-AI מנתח את היומן שלך לשליפת תובנות..."})

def send_main_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], [{"text": "🎰 קזינו"}, {"text": "🤖 ניתוח יומן"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND ELITE SUPREME**\nהמערכת פעילה ומוכנה.", "reply_markup": kb})
