import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import update_user_balance, get_user_stats, get_total_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # משחקי אנימציה - זיהוי תוצאה ומתן XP/SLH
    if dice:
        v, e = dice.get("value"), dice.get("emoji")
        win = 500 if (e == "🎰" and v in [1, 22, 43, 64]) or (e == "🎲" and v == 6) else 0
        if win > 0:
            update_user_balance(user_id, win)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎉 ניצחון! קיבלת {win} SLH וצברת XP!"})
        return

    # פקודת START עם מערכת שותפים
    if text.startswith("/start"):
        ref_id = text.split(" ")[1] if len(text.split(" ")) > 1 else None
        # כאן אפשר להוסיף לוגיקה של רישום רפראל ב-DB
        
        msg = "💎 **DIAMOND ELITE PRO - המערכת המלאה**\n\nברוך הבא לעוזר הפיננסי שלך.\nהשתמש בתפריט לביצוע פעולות:"
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק וניהול נכסים (Mini App)", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI PRO - מדריך ויועץ (39)", "callback_data": "ai_pro_offer"}],
            [{"text": "🎰 משחקי אנימציה", "callback_data": "games_menu"}, {"text": "📈 יומן שוק", "callback_data": "view_journal"}],
            [{"text": "🏆 מובילים", "callback_data": "leaderboard"}, {"text": "👥 שותפים ו-Earn", "callback_data": "referral_info"}]
        ]}
        if user_id == str(ADMIN_ID):
            kb["inline_keyboard"].append([{"text": "📊 דאשבורד מנהל", "callback_data": "admin_stats"}])
        
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "ai_pro_offer":
        msg = ("💰 **מסלול AI PRO - עוזר אישי ללא הגבלה**\n\n"
               "בתשלום חד-פעמי של **39 ש''ח** תקבל:\n"
               "1️⃣ מדריך מקיף ליצירת רווחים עם ה-AI של הבוט.\n"
               "2️⃣ עוזר טכני צמוד לניהול תיקי השקעות.\n"
               "3️⃣ לימוד שוק ההון ומסחר קריפטו ב-Real-time.\n\n"
               "להפעלה: שלח הודעה לאדמין או העבר TON לארנק המערכת.")
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "games_menu":
        kb = {"inline_keyboard": [
            [{"text": "🎰 סלוט", "callback_data": "dice_🎰"}, {"text": "🎲 קוביה", "callback_data": "dice_🎲"}],
            [{"text": "🏀 כדורסל", "callback_data": "dice_🏀"}, {"text": "🎯 חיצים", "callback_data": "dice_🎯"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק מהיר בצ'אט:", "reply_markup": kb})

    elif data.startswith("dice_"):
        emoji = data.split("_")[1]
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": emoji})

    elif data == "leaderboard":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📊 **טבלת מובילים:**\n1. Osif - 50k SLH\n2. User224 - 12k SLH"})

    elif data == "view_journal":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "📝 **יומן שוק:**\nשמרת 3 תובנות על ביטקוין ו-TON בשבוע האחרון."})

    elif data == "referral_info":
        link = f"t.me/YourBotName?start={user_id}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"👥 **תוכנית שותפים:**\nעל כל חבר תקבל 500 SLH!\n\nלינק להזמנה: {link}", "parse_mode": "Markdown"})
