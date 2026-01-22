import requests, sqlite3, logging, os, random
from utils.config import *

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
ADMIN_ID = str(os.getenv('ADMIN_ID'))
WIN_CHANCE = int(os.getenv('WIN_CHANCE_PERCENT', 30)) # סיכוי זכייה מה-Railway

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def update_rank(xp):
    if xp > 2000: return "💎 DIAMOND"
    if xp > 500: return "🏅 ELITE"
    return "🥉 STARTER"

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice") # תמיכה בשליחת אימוג'י של קוביה

    # --- מנגנון קזינו (כששולחים קוביה) ---
    if dice:
        conn = get_db(); c = conn.cursor()
        user = c.execute("SELECT balance, xp FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
        # הגרלה לפי אחוז הזכייה שהגדרת
        is_winner = random.randint(1, 100) <= WIN_CHANCE
        reward = 200 if is_winner else 0
        xp_gain = 15
        
        new_rank = update_rank(user['xp'] + xp_gain)
        
        c.execute("UPDATE users SET balance = balance + ?, xp = xp + ?, rank = ? WHERE user_id = ?", 
                  (reward, xp_gain, new_rank, user_id))
        conn.commit(); conn.close()

        result_text = f"🎉 זכית ב-{reward} SLH!" if is_winner else "❌ הפעם לא זכית, נסה שוב!"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, 
            "text": f"{result_text}\n🏆 XP: +{xp_gain} | דרגה נוכחית: {new_rank}"
        })
        return

    if not text: return

    # --- פקודות אדמין ---
    if user_id == ADMIN_ID:
        if text.startswith("/set_chance "):
            global WIN_CHANCE
            WIN_CHANCE = int(text.split()[1])
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"⚙️ סיכוי הזכייה עודכן ל-{WIN_CHANCE}%"})
            return
        elif text.startswith("/broadcast "):
            msg = text.replace("/broadcast ", "")
            conn = get_db(); users = conn.execute("SELECT user_id FROM users").fetchall()
            for u in users:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": u['user_id'], "text": f"📢 **LIVE UPDATE:**\n{msg}"})
            return

    # --- תפריט משתמש ---
    if text == "/start":
        conn = get_db(); c = conn.cursor()
        if not c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchone():
            c.execute("INSERT INTO users (user_id, balance, xp, rank) VALUES (?, 100, 0, 'Starter')", (user_id,))
            conn.commit()
        send_menu(chat_id)

    elif text == "🎰 קזינו":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, 
            "text": "🎲 **ברוכים הבאים לקזינו!**\nשלחו עכשיו את אימוג'י הקוביה (🎲) כדי לנסות את מזלכם!\n\nסיכוי זכייה נוכחי: " + str(WIN_CHANCE) + "%"
        })

    elif text == "💳 הארנק שלי":
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        msg = f"👤 **פרופיל משתמש**\n💰 יתרה: {user['balance']} SLH\n🏆 XP: {user['xp']}\n🏅 דרגה: {user['rank']}"
        kb = {"inline_keyboard": [[{"text": "💰 פתח אפליקציה", "web_app": {"url": f"https://{os.getenv('RAILWAY_STATIC_URL')}/"}}, {"text": "📥 הפקדה", "callback_data": "dep"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

def send_menu(chat_id):
    kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], [{"text": "🎰 קזינו"}, {"text": "🤖 ניתוח יומן"}]], "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "💎 **DIAMOND SUPREME**\nהמערכת מוכנה למשחק.", "reply_markup": kb})

def handle_callback(callback_query):
    # פונקציה זו נשארת לטיפול בהפקדות כפי שהיה ב-v23
    pass
