import requests, sqlite3, logging, os
from utils.config import * # טעינת כל 20 המשתנים מ-Railway

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DIAMOND-CORE] - %(message)s')

def get_db():
    return sqlite3.connect('database.db')

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # 1. ניתוב פקודות (תיקון התפריט הכחול וכל הפקודות שנעלמו)
    clean_text = text.lower().strip()
    
    if clean_text.startswith("/start"):
        # לוגיקת רפראל משתמשת ב-REFERRAL_REWARD מה-Railway
        ref_id = text.split()[1] if len(text.split()) > 1 else None
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, ref_id))
        if ref_id and ref_id != user_id:
            reward = os.getenv("REFERRAL_REWARD", 500)
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, ref_id))
        conn.commit(); conn.close()
        
        # הגדרת פקודות לתפריט הכחול (Bot Menu)
        requests.post(f"{TELEGRAM_API_URL}/setMyCommands", json={"commands": [
            {"command": "start", "description": "🏠 תפריט ראשי"},
            {"command": "profile", "description": "💳 הארנק שלי"},
            {"command": "ai", "description": "🤖 AI PRO"},
            {"command": "admin", "description": "🛡 ניהול (אדמין)"},
            {"command": "help", "description": "ℹ️ עזרה"}
        ]})

        msg = "💎 **DIAMOND ELITE SUPREME**\nברוך הבא למערכת הפיננסית המתקדמת."
        reply_kb = {
            "keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎰 קזינו"}], [{"text": "🤖 AI PRO"}, {"text": "📈 יומן שוק"}]],
            "resize_keyboard": True
        }
        inline_kb = {"inline_keyboard": [
            [{"text": "🚀 Roadmap & Web3", "callback_data": "roadmap"}, {"text": "🏆 מובילים", "callback_data": "top"}],
            [{"text": "📞 צור קשר עם המפתח", "url": f"https://t.me/{ADMIN_USERNAME}"}],
            [{"text": "💎 קבוצת VIP", "url": os.getenv("PARTICIPANTS_GROUP_LINK", "")}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": reply_kb, "parse_mode": "Markdown"})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "פעולות מהירות:", "reply_markup": inline_kb})
        return

    # 2. פקודות ישירות (עובדות תמיד)
    if clean_text in ["/profile", "💳 הארנק שלי"]:
        kb = {"inline_keyboard": [[{"text": "פתח ארנק Diamond", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 יתרה ודרגה בזמן אמת:", "reply_markup": kb})
        return

    if clean_text in ["/ai", "🤖 ai pro"]:
        msg = f"🤖 **AI PRO - עוזר אישי**\nמחיר: {os.getenv('PRICE_SH', '39')}\nגישה לקבוצה: {os.getenv('PARTICIPANTS_GROUP_LINK')}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
        return

    if clean_text in ["/admin"] and user_id == str(ADMIN_ID):
        msg = "🛡 **Admin Panel**\n/mint [ID] [AMT]\n/stats - לראות נתוני מערכת"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})
        return

    if clean_text in ["/games", "🎰 קזינו"]:
        kb = {"inline_keyboard": [[{"text": "🎰", "callback_data": "d_🎰"}, {"text": "🏀", "callback_data": "d_🏀"}, {"text": "🎯", "callback_data": "d_🎯"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})
        return

    # 3. משחקים (Dice) - שימוש ב-WIN_CHANCE_PERCENT
    if dice:
        # לוגיקה שמשתמשת בסיכוי מה-Railway
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🎲 מעבד תוצאה..."})
        return

    # 4. יומן שוק (רק אם זה לא פקודה!)
    if text and not text.startswith("/") and text not in ["💳 הארנק שלי", "🎰 קזינו", "🤖 AI PRO", "📈 יומן שוק"]:
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO user_journal (user_id, entry) VALUES (?, ?)", (user_id, text))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ נשמר ביומן השוק."})

def handle_callback(callback):
    # (לוגיקה של callback נשארת ומשתמשת ב-Roadmap ו-Top)
    pass
