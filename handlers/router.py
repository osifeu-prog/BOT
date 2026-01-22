import requests, sqlite3, logging, os, random, time
from datetime import datetime, timedelta
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- לוגיקת סוכן השקעות (Investment Insights) ---
def get_ai_insights(user_id):
    conn = get_db()
    entries = conn.execute("SELECT entry FROM user_journal WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user_id,)).fetchall()
    conn.close()
    if not entries: return "אין מספיק נתונים ביומן כדי לנתח את התיק שלך. התחל לרשום פעולות שוק!"
    
    summary = " ".join([e['entry'] for e in entries])
    # כאן יבוא חיבור ל-OpenAI. כרגע כסוכן "חכם" מובנה:
    return f"🔍 **ניתוח סוכן חכם:** מזהה התעניינות ב-{summary[:30]}... מומלץ לעקוב אחרי רמות תמיכה ב-TON."

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    if not text: return

    # --- פקודות אדמין ---
    if user_id == ADMIN_ID:
        if text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "")
            conn = get_db(); users = conn.execute("SELECT user_id FROM users").fetchall()
            for u in users: requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": u['user_id'], "text": f"📢 **עדכון שוק מיוחד:**\n{msg}"})
            return

    # --- הצטרפות ושותפים (Affiliates) ---
    if text.startswith("/start"):
        conn = get_db(); c = conn.cursor()
        user = c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user:
            # בדיקת רפרל/מתנה
            args = text.split()
            bonus = 500 if (len(args) > 1 and "gift" in args[1]) else 100
            c.execute("INSERT INTO users (user_id, balance, xp, rank) VALUES (?, ?, 0, 'Starter')", (user_id, bonus))
            conn.commit()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ADMIN_ID, "text": f"🔔 משתמש חדש הצטרף: {user_id}"})
        conn.close()
        send_menu(chat_id)

    # --- ניהול פורטפוליו וארנק ---
    elif text == "💳 הארנק שלי":
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        msg = f"📊 **תיק השקעות ופרופיל**\n\n💰 יתרה זמינה: {user['balance']} SLH\n🏆 XP: {user['xp']}\n🏅 דרגה: {user['rank']}\n💎 VIP: {'פעיל' if user['is_vip'] else 'לא פעיל'}\n\n🔗 לינק שותפים: https://t.me/{(requests.get(f'{TELEGRAM_API_URL}/getMe').json()['result']['username'])}?start={user_id}"
        kb = {"inline_keyboard": [[{"text": "📥 הפקדה (TON)", "callback_data": "dep"}, {"text": "📤 משיכה", "callback_data": "with"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    # --- סוכן השקעות AI ---
    elif text == "🤖 סוכן חכם (AI)":
        insight = get_ai_insights(user_id)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": insight})

    # --- בונוס יומי (עם חסימה ל-24 שעות) ---
    elif text == "🎁 בונוס יומי":
        conn = get_db(); c = conn.cursor()
        user = c.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,)).fetchone()
        now = datetime.now()
        if user['last_daily'] and datetime.strptime(user['last_daily'], '%Y-%m-%d %H:%M:%S') > now - timedelta(days=1):
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "⏳ הבונוס יהיה זמין שוב מחר!"})
        else:
            c.execute("UPDATE users SET balance = balance + 100, last_daily = ? WHERE user_id = ?", (now.strftime('%Y-%m-%d %H:%M:%S'), user_id))
            conn.commit()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎁 קיבלת 100 SLH! נתראה מחר."})
        conn.close()

    elif text == "🎰 ארקייד":
        send_arcade_menu(chat_id)

    elif text.startswith("💰 הימור:"):
        amt = text.split(":")[1].split()[0]
        send_guess_buttons(chat_id, amt)

    # --- יומן שוק (הזנת נתונים לסוכן) ---
    else:
        conn = get_db(); conn.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📝 רשמתי ביומן השוק. הסוכן החכם ינתח זאת."})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = str(callback_query.get("from", {}).get("id"))
    data = callback_query.get("data")

    if data.startswith("play_"):
        # לוגיקת הקוביה (כפי שהייתה ב-v27, מוטמעת כאן במלואה)
        process_bet(chat_id, user_id, data)
    elif data == "dep":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📥 שלח TON לכתובת:\n{os.getenv('TON_WALLET')}", "parse_mode": "Markdown"})

def send_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🤖 סוכן חכם (AI)"}], [{"text": "🎰 ארקייד"}, {"text": "🎁 בונוס יומי"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND SUPREME INVEST**\nברוך הבא לסוכן ההשקעות הפרטי שלך.", "reply_markup": kb})

def send_arcade_menu(chat_id):
    kb = {"keyboard": [[{"text": "💰 הימור: 50 SLH"}, {"text": "💰 הימור: 100 SLH"}], [{"text": "🔙 חזרה"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎰 **בחר סכום הימור:**", "reply_markup": kb})

def send_guess_buttons(chat_id, amt):
    btns = [[{"text": f"🎲 {i}", "callback_data": f"play_{amt}_{i}"} for i in range(1, 4)],
            [{"text": f"🎲 {i}", "callback_data": f"play_{amt}_{i}"} for i in range(4, 7)]]
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"מהמר על {amt} SLH. נחש מספר:", "reply_markup": {"inline_keyboard": btns}})

def process_bet(chat_id, user_id, data):
    _, amt, guess = data.split("_")
    amt, guess = int(amt), int(guess)
    conn = get_db(); user = conn.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if user['balance'] < amt:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ אין מספיק SLH!"})
        return
    conn.execute("UPDATE users SET balance = balance - ?, xp = xp + 10 WHERE user_id = ?", (amt, user_id))
    conn.commit()
    dice_msg = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"}).json()
    val = dice_msg['result']['dice']['value']
    time.sleep(3.5)
    win_chance = int(os.getenv('WIN_CHANCE_PERCENT', 30))
    if val == guess and random.randint(1, 100) <= win_chance:
        win = amt * 5
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win, user_id))
        res = f"🎯 בול! זכית ב-{win} SLH!"
    else: res = f"❌ יצא {val}. הפסדת {amt}."
    conn.commit(); conn.close()
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": res})
