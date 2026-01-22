import requests, sqlite3, logging, os, uuid
from utils.config import *

logging.basicConfig(level=logging.INFO)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def log_tx(user_id, amount, tx_type, desc):
    conn = get_db(); c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)", 
              (user_id, amount, tx_type, desc))
    conn.commit(); conn.close()

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # --- 1. מנגנון משחקים ו-XP (שימוש ב-WIN_CHANCE_PERCENT) ---
    if dice:
        val, emo = dice.get("value"), dice.get("emoji")
        win = 500 if val >= 5 else 0
        conn = get_db(); c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ?, xp = xp + 10 WHERE user_id = ?", (win, user_id))
        conn.commit(); conn.close()
        if win > 0:
            log_tx(user_id, win, "GAME", f"Win on {emo}")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎉 בום! +{win} SLH וצברת 10 XP!"})
        return

    # --- 2. סינון פקודות למניעת רישום ביומן ---
    nav_buttons = ["💳 הארנק שלי", "🎰 קזינו", "🤖 AI PRO", "📈 יומן שוק"]
    if text.startswith("/") or text in nav_buttons:
        execute_command(chat_id, user_id, text)
    else:
        # יומן שוק נקי
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נרשם ביומן השוק. שלח /ai לניתוח."})

def execute_command(chat_id, user_id, text):
    cmd = text.lower()

    if "/start" in cmd:
        # לוגיקת אפילייטס (Referral)
        args = text.split()
        if len(args) > 1:
            ref_id = args[1]
            if ref_id != user_id:
                conn = get_db(); c = conn.cursor()
                c.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
                if not c.fetchone():
                    reward = int(os.getenv("REFERRAL_REWARD", 500))
                    c.execute("INSERT INTO users (user_id, referred_by, balance) VALUES (?, ?, ?)", (user_id, ref_id, 0))
                    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, ref_id))
                    log_tx(ref_id, reward, "REFERRAL", f"Invite bonus for {user_id}")
                    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ref_id, "text": f"👥 חבר הצטרף! קיבלת {reward} SLH!"})
                conn.commit(); conn.close()

        # הגדרת תפריט כחול (Bot Command Menu)
        requests.post(f"{TELEGRAM_API_URL}/setMyCommands", json={"commands": [
            {"command": "start", "description": "🏠 בית"}, {"command": "profile", "description": "💳 ארנק"},
            {"command": "ai", "description": "🤖 AI"}, {"command": "admin", "description": "🛡 ניהול"}
        ]})

        msg = "💎 **DIAMOND ELITE SUPREME**\nהאקו-סיסטם שלך מוכן."
        reply_kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎰 קזינו"}], [{"text": "🤖 AI PRO"}, {"text": "📈 יומן שוק"}]], "resize_keyboard": True}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": reply_kb, "parse_mode": "Markdown"})

    elif "ארנק" in cmd or "/profile" in cmd:
        # פתיחה ישירה של מיני אפ
        kb = {"inline_keyboard": [[{"text": "💰 פתח ארנק מלא", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **ניהול נכסים:**\nצפה ביתרה, היסטוריה ודרגה.", "reply_markup": kb})

    elif "/admin" in cmd and user_id == str(ADMIN_ID):
        msg = "🛡 **פאנל אדמין:**\n/mint [ID] [AMT] - הנפקה\n/stats - סטטיסטיקה מלאה\n/vip [ID] - מתן גישה ל-AI\n/send [AMT] [ID] - שליחת כסף"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    elif "/stats" in cmd and user_id == str(ADMIN_ID):
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        users = c.fetchone()[0]
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='MINT'")
        minted = c.fetchone()[0] or 0
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📊 **נתוני מערכת:**\n👥 משתמשים: {users}\n💎 הונפקו: {minted} SLH"})

    elif "/mint" in cmd and user_id == str(ADMIN_ID):
        try:
            _, target, amt = text.split()
            conn = get_db(); c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(amt), target))
            conn.commit(); conn.close()
            log_tx(target, int(amt), "MINT", "Admin issuance")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"✅ הונפקו {amt} SLH ל-{target}"})
        except: pass
