import requests, sqlite3, logging, os
from utils.config import *

def get_db():
    return sqlite3.connect('database.db')

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")

    # --- פקודת Broadcast (אדמין בלבד) ---
    if text.startswith("/broadcast") and user_id == str(ADMIN_ID):
        msg_to_send = text.replace("/broadcast", "").strip()
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        for u in users:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": u[0], "text": f"📢 **עדכון LIVE:**\n{msg_to_send}", "parse_mode": "Markdown"})
        return

    # --- רכישת AI PRO ---
    if text == "💳 רכישת מנוי AI":
        price = int(os.getenv("PRICE_SH", 39))
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        balance = c.fetchone()[0]
        if balance >= price:
            c.execute("UPDATE users SET balance = balance - ?, is_vip = 1 WHERE user_id = ?", (price, user_id))
            conn.commit()
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"✅ המנוי הופעל! הלינק לקבוצה:\n{os.getenv('PARTICIPANTS_GROUP_LINK')}"})
        else:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "❌ אין מספיק SLH בארנק."})
        conn.close()
        return

    # --- שאר הפקודות (Start, Wallet, etc.) נשארות ומתעדכנות ---
    if text == "/start":
        # הצגת נתונים עם Rank ו-XP
        # (כפי שכתבנו ב-v19 עם שכלול ה-Broadcast האחרון)
        pass
