import requests, sqlite3, logging, os, random, time
from datetime import datetime, timedelta
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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
            for u in users:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": u['user_id'], "text": f"📢 **הודעה מערכת:**\n{msg}"})
            return

    # --- תפריט ראשי ---
    if text == "/start":
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, balance, xp, rank) VALUES (?, 200, 0, 'Starter')", (user_id,))
        conn.commit(); conn.close()
        send_menu(chat_id)

    elif text == "💳 הארנק שלי":
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        msg = f"👤 **פרופיל**\n💰 יתרה: {user['balance']} SLH\n🏅 דרגה: {user['rank']}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    elif text == "🎰 ארקייד":
        kb = {"keyboard": [[{"text": "💰 הימור: 10 SLH"}, {"text": "💰 הימור: 50 SLH"}], [{"text": "💰 הימור: 100 SLH"}, {"text": "🔙 חזרה"}]], "resize_keyboard": True}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎮 **בחר סכום הימור בקוביה:**", "reply_markup": kb})

    elif text.startswith("💰 הימור:"):
        amount = text.split(":")[1].split()[0]
        send_guess_buttons(chat_id, amount)

    elif text == "🎁 בונוס יומי":
        conn = get_db(); c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + 100 WHERE user_id = ?", (user_id,))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ קיבלת 100 SLH בונוס!"})

    else:
        # רישום יומן שוק
        conn = get_db(); conn.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📝 נרשם ביומן השוק."})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = str(callback_query.get("from", {}).get("id"))
    data = callback_query.get("data")

    if data.startswith("play_"): # play_amount_guess
        _, amt, guess = data.split("_")
        amt, guess = int(amt), int(guess)
        
        conn = get_db(); user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if user['balance'] < amt:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ אין לך מספיק SLH!"})
            return

        # חיוב וזריקת קוביה
        conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amt, user_id))
        conn.commit()
        
        dice_msg = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"}).json()
        result = dice_msg['result']['dice']['value']
        
        time.sleep(3.5)
        
        if result == guess:
            win = amt * 5
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win, user_id))
            conn.commit()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎯 בול! יצא {result}. זכית ב-{win} SLH!"})
        else:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"❌ יצא {result}. הניחוש היה {guess}. הפסדת {amt} SLH."})
        conn.close()

def send_guess_buttons(chat_id, amt):
    btns = []
    row = []
    for i in range(1, 7):
        row.append({"text": f"🎲 {i}", "callback_data": f"play_{amt}_{i}"})
        if len(row) == 3: btns.append(row); row = []
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"בחרת להמר על {amt} SLH. נחש מה ייצא:", "reply_markup": {"inline_keyboard": btns}})

def send_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], [{"text": "🎰 ארקייד"}, {"text": "🤖 ניתוח יומן"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND SUPREME SYSTEM**", "reply_markup": kb})
