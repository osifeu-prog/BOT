import requests, sqlite3, logging, os, random, time
from datetime import datetime, timedelta
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- מערכת הדרגות וה-VIP ---
def get_user_status(xp, is_vip):
    rank = "🥉 Starter"
    if xp > 500: rank = "🥈 Advanced"
    if xp > 2000: rank = "🥇 Expert"
    if xp > 5000: rank = "💎 Diamond"
    vip_status = "✨ VIP" if is_vip else "Standard"
    return rank, vip_status

# --- סוכן השקעות מתקדם (Portfolio & Risk) ---
def get_investment_report(user_id):
    conn = get_db()
    journal = conn.execute("SELECT entry FROM user_journal WHERE user_id = ? ORDER BY id DESC LIMIT 15", (user_id,)).fetchall()
    user = conn.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not journal: return "אין מספיק נתונים ביומן. רשום קניות/מכירות כדי לקבל דוח."
    
    report = f"📋 **דוח סוכן חכם:**\n\n"
    report += f"💰 יתרה נוכחית: {user['balance']} SLH\n"
    report += "🔍 תובנות: המשתמש מדווח על פעילות בנכסים דיגיטליים. "
    if user['balance'] < 100: report += "⚠️ אזהרת סיכון: יתרה נמוכה לביצוע פעולות חדשות."
    return report

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    if not text: return

    # --- פקודות אדמין (Admin Menu) ---
    if user_id == ADMIN_ID:
        if text == "/admin":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🛠 **תפריט ניהול:**\n/stats - סטטיסטיקה\n/broadcast [msg] - הודעה לכולם\n/give_vip [id] - הענקת VIP"})
            return

    # --- תפריט משתמש ראשי ---
    if text.startswith("/start"):
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, balance, xp, rank) VALUES (?, 200, 0, 'Starter')", (user_id,))
        conn.commit(); conn.close()
        send_main_menu(chat_id)

    elif text == "💳 הפורטפוליו שלי":
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        rank, vip = get_user_status(u['xp'], u['is_vip'])
        msg = f"👤 **פרופיל משקיע**\n\n💎 סטטוס: {vip}\n🏅 דרגה: {rank}\n💰 יתרה: {u['balance']} SLH\n🏆 XP: {u['xp']}"
        kb = {"inline_keyboard": [[{"text": "📥 הפקדה", "callback_data": "dep"}, {"text": "📤 משיכה", "callback_data": "with"}],
                                   [{"text": "🏆 Leaderboard", "callback_data": "lead"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb})

    elif text == "🤖 סוכן (AI)":
        report = get_investment_report(user_id)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": report})

    elif text == "🕹 Arcade":
        send_arcade_menu(chat_id)

    elif text.startswith("💰 Bet:"):
        amt = text.split(":")[1].split()[0]
        send_guess_buttons(chat_id, amt)

    elif text == "🎁 Daily":
        process_daily(chat_id, user_id)

    else:
        # רישום יומן (Data for AI)
        conn = get_db(); conn.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ רשום ביומן השוק. הסוכן מעבד את הנתונים."})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    user_id = str(callback_query.get("from", {}).get("id"))
    data = callback_query.get("data")

    if data.startswith("p_"): # p_[amt]_[guess]
        process_arcade_play(chat_id, user_id, data)
    elif data == "lead":
        conn = get_db()
        top = conn.execute("SELECT user_id, xp FROM users ORDER BY xp DESC LIMIT 5").fetchall()
        msg = "🏆 **מובילי הקהילה:**\n" + "\n".join([f"{i+1}. {u['user_id']}: {u['xp']} XP" for i, u in enumerate(top)])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

def send_main_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הפורטפוליו שלי"}, {"text": "🤖 סוכן (AI)"}], 
                       [{"text": "🕹 Arcade"}, {"text": "🎁 Daily"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND ELITE v3.0**", "reply_markup": kb})

def send_arcade_menu(chat_id):
    kb = {"keyboard": [[{"text": "💰 Bet: 10 SLH"}, {"text": "💰 Bet: 50 SLH"}], [{"text": "🔙 חזרה"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🕹 **בחר סכום הימור:**", "reply_markup": kb})

def send_guess_buttons(chat_id, amt):
    btns = [[{"text": f"🎲 {i}", "callback_data": f"p_{amt}_{i}"} for i in range(1, 4)],
            [{"text": f"🎲 {i}", "callback_data": f"p_{amt}_{i}"} for i in range(4, 7)]]
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"נחש מספר (הימור {amt}):", "reply_markup": {"inline_keyboard": btns}})

def process_arcade_play(chat_id, user_id, data):
    # לוגיקת משחק מלאה כולל עדכון XP ודרגה
    _, amt, guess = data.split("_")
    amt, guess = int(amt), int(guess)
    conn = get_db(); u = conn.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if u['balance'] < amt:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ אין מספיק SLH!"})
        return
    
    # אנימציה
    dice = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"}).json()
    val = dice['result']['dice']['value']
    time.sleep(3.5)
    
    win = (val == guess) and (random.randint(1, 100) <= int(os.getenv('WIN_CHANCE_PERCENT', 30)))
    if win:
        reward = amt * 5
        conn.execute("UPDATE users SET balance = balance + ?, xp = xp + 50 WHERE user_id = ?", (reward, user_id))
        msg = f"🎯 בול! זכית ב-{reward} SLH!"
    else:
        conn.execute("UPDATE users SET balance = balance - ?, xp = xp + 5 WHERE user_id = ?", (amt, user_id))
        msg = f"❌ יצא {val}. הפסדת {amt} SLH."
    conn.commit(); conn.close()
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

def process_daily(chat_id, user_id):
    conn = get_db(); c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + 100, xp = xp + 20 WHERE user_id = ?", (user_id,))
    conn.commit(); conn.close()
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎁 קיבלת 100 SLH ו-20 XP!"})
