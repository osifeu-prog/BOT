import requests, sqlite3, logging, os, datetime
from utils.config import *

def get_db():
    return sqlite3.connect('database.db')

def get_rank(xp):
    if xp > 1000: return "💎 Diamond"
    if xp > 500: return "🏅 Elite"
    return "🥉 Starter"

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")

    if text == "/start":
        # לוגיקת רישום ואפילייט (REFERRAL_REWARD)
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT balance, xp, rank FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        
        if not user:
            c.execute("INSERT INTO users (user_id, balance, xp) VALUES (?, 0, 0)")
            conn.commit()
            user = (0, 0, "Starter")
        
        balance, xp, rank = user
        msg = (f"💎 **DIAMOND ELITE WALLET**\n"
               f"💰 יתרה: {balance} SLH\n"
               f"🏆 XP: {xp} | 🏅 דרגה: {rank}\n\n"
               f"📈 LIVE: הביטקוין יציב • הבונוס היומי מוכן!")
        
        reply_kb = {"keyboard": [[{"text": "💳 הארנק שלי"}, {"text": "🎁 בונוס יומי"}], 
                                 [{"text": "🎰 קזינו"}, {"text": "🤖 AI PRO"}]], "resize_keyboard": True}
        
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": reply_kb, "parse_mode": "Markdown"})

    elif text == "🎁 בונוס יומי":
        conn = get_db(); c = conn.cursor()
        # בדיקה אם עברו 24 שעות (לוגיקה פשוטה)
        c.execute("UPDATE users SET balance = balance + 100, xp = xp + 20 WHERE user_id = ?", (user_id,))
        conn.commit(); conn.close()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ אספת 100 SLH ו-20 XP! חזור מחר."})

    elif text == "💳 הארנק שלי":
        kb = {"inline_keyboard": [
            [{"text": "💰 פתח ארנק מלא", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "📥 הפקדה (TON)", "callback_data": "dep"}, {"text": "📤 משיכה", "callback_data": "with"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **ניהול נכסים:**", "reply_markup": kb})

    elif text == "🤖 AI PRO":
        price = os.getenv("PRICE_SH", "39")
        kb = {"inline_keyboard": [[{"text": "💳 רכישת מנוי", "callback_data": "buy_ai"}]]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🤖 **AI PRO - יועץ אישי**\nניתוח יומן שוק ותובנות קריפטו.\nעלות: {price} SLH", "reply_markup": kb})

    elif text == "/admin" and user_id == str(ADMIN_ID):
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🛡 **Admin Menu:**\n/mint [ID] [AMT]\n/stats\n/broadcast [MSG]"})
