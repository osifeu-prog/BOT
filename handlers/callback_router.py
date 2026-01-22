import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, TON_WALLET
from db.users import get_user_stats, get_leaderboard

async def handle_callback(callback_query):
    user_id = callback_query.get("from", {}).get("id")
    chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
    data = callback_query.get("data", "")
    call_id = callback_query.get("id")

    # אישור קבלת הלחיצה (מוריד את השעון המסתובב)
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": call_id})

    if data == "ai_chat":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **מערכת ה-AI זמינה!**\nשאל אותי כל דבר על שוק ההון או קריפטו."})
    
    elif data == "show_leaderboard":
        leaders = get_leaderboard()
        txt = "🏆 **טבלת 10 המובילים:**\n\n" + "\n".join([f"{i+1}. {u[0]}: {u[1]} SLH" for i, u in enumerate(leaders)])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": txt})

    elif data == "payment_info":
        msg = f"💳 **רכישת SLH:**\n\n1. העתק את הארנק:\n{TON_WALLET}\n2. שלח את הסכום המבוקש.\n3. שלח צילום מסך לאדמין."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
    
    elif data == "admin_main" and str(user_id) == str(ADMIN_ID):
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "👑 **שלום אדמין.**\nהמערכת מסונכרנת. השתמש ב-/admin לצפייה בנתונים."})
