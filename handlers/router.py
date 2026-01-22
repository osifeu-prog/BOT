import requests
import time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, BOT_USERNAME
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats, transfer_slh, get_leaderboard

# מנגנון הגנה נגד הצפות (פשוט)
user_cooldowns = {}

async def handle_message(message):
    user_id = str(message["from"]["id"])
    now = time.time()
    
    # הגנה: מקסימום הודעה כל 1.5 שניות
    if user_id in user_cooldowns and now - user_cooldowns[user_id] < 1.5:
        return
    user_cooldowns[user_id] = now

    text = message.get("text", "")

    # טבלת מובילים (Leaderboard)
    if text == "📊 טבלת מובילים" or text == "/top":
        top = get_leaderboard()
        leader_text = "🏆 **חמשת הלווייתנים של Diamond VIP:**\n\n"
        for i, user in enumerate(top):
            leader_text += f"{i+1}. משתמש {user[0][:4]}... - 🪙 {user[1]} SLH\n"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": leader_text, "parse_mode": "Markdown"})
        return

    # Deep Linking: העברה ויראלית בטוחה
    if text.startswith("/start pay_"):
        target_id = text.split("_")[1]
        if target_id == user_id:
            msg = "❌ ניסיון יפה, אבל אי אפשר לשלוח כסף לעצמך!"
        else:
            if transfer_slh(user_id, target_id, 50):
                msg = f"✅ **העברה בוצעה!**\nשלחת 50 SLH לכתובת {target_id}."
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": target_id, "text": f"🎁 קיבלת 50 SLH מחבר ({user_id})!"})
            else:
                msg = "❌ יתרה נמוכה מדי לביצוע העברה."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})
        return

    # שאר התפריטים (START וכו')...
    if text == "/start" or text == "🔙 חזרה":
        welcome = (f"💎 **ברוך הבא ל-Diamond Arcade VIP** 💎\n\n"
                  f"כאן הכסף שלך עובד בשבילך (ובשביל הכיף!)\n"
                  f"🎮 משחקים, 🪙 מרוויחים ו-🤝 משתפים.")
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": welcome, "parse_mode": "Markdown",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "מה נרצה לעשות עכשיו?",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
