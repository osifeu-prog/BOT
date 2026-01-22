import requests, random
from utils.config import TELEGRAM_API_URL, ADMIN_ID
from db.users import update_user_balance, get_user_stats, get_total_stats

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")
    dice = message.get("dice")

    # טיפול במשחקי אנימציה של טלגרם (קוביה, סלוט וכו')
    if dice:
        value = dice.get("value")
        emoji = dice.get("emoji")
        win_amount = 0
        if emoji == "🎰" and value in [1, 22, 43, 64]: win_amount = 500  # זכייה בסלוט
        elif emoji == "🎲" and value == 6: win_amount = 100 # זכייה בקוביה
        
        if win_amount > 0:
            update_user_balance(user_id, win_amount)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎉 מטורף! זכית ב-{win_amount} SLH!"})
        return

    # פקודות
    if text.startswith("/start"):
        msg = "💎 **DIAMOND ELITE SYSTEM v8.0**\nהכל מחובר ופעיל."
        kb = {"inline_keyboard": [
            [{"text": "💳 הארנק שלי (Mini-App)", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI עוזר אישי", "callback_data": "ai_info"}, {"text": "🏆 מובילים", "callback_data": "leaderboard"}],
            [{"text": "🎰 משחקי אנימציה", "callback_data": "dice_games"}, {"text": "👥 שותפים", "callback_data": "ref_info"}]
        ]}
        if str(user_id) == str(ADMIN_ID):
            kb["inline_keyboard"].append([{"text": "⚙️ פאנל ניהול", "callback_data": "admin_report"}])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

    # AI חופשי - עונה על הכל
    elif text and not text.startswith("/"):
        res = f"🤖 **עוזר AI:**\nלגבי '{text}' - הנה ניתוח קצר...\n(כאן יופיע ניתוח מעמיק מהמנוע המחובר)"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": res})

def handle_callback(callback_query):
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query['id']})
    
    if data == "dice_games":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "שלח עכשיו את האימוג'י 🎰 או 🎲 לצ'אט כדי לשחק!"})
    elif data == "admin_report":
        s = get_total_stats()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"📊 דוח: {s[0]} משתמשים."})
