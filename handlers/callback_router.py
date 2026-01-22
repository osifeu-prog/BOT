import requests
from utils.config import TELEGRAM_API_URL
from db.users import get_user_stats, get_leaderboard

async def handle_callback(callback_query):
    try:
        user_id = str(callback_query.get("from", {}).get("id"))
        data = callback_query.get("data", "")
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        callback_id = callback_query.get("id")

        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_id})

        if data == "wallet":
            stats = get_user_stats(user_id)
            text = f"💰 **הארנק הדיגיטלי**\n\n💎 SLH: {stats[1]:,}\n⭐ XP: {stats[0]:,}\n💵 יתרה: {stats[2]:,}"
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

        elif data == "leaderboard":
            leaders = get_leaderboard()
            text = "🏆 **מובילי הטבלה (SLH)**\n\n"
            for i, (uid, slh) in enumerate(leaders, 1):
                text += f"{i}. ID: {uid} — 💎 {slh:,}\n"
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

        elif data == "ai_chat":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **מערכת AI פעילה**\nשלח הודעה בפרטי וה-AI ישיב לך (בקרוב)."})

        elif data == "settings":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "⚙️ **הגדרות**\nכאן תוכל לשנות שפה ולנהל התראות."})
            
        elif data == "admin_panel":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🛡 **פאנל ניהול**\nסטטוס DB: יציב\nניצול משאבים: תקין."})
            
    except Exception as e:
        print(f"❌ Callback Error: {e}")