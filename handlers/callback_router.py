import requests
from utils.config import TELEGRAM_API_URL
from db.users import get_user_stats

async def handle_callback(callback_query):
    try:
        user_id = str(callback_query.get("from", {}).get("id"))
        data = callback_query.get("data", "")
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        callback_id = callback_query.get("id")

        # אישור קבלת הלחיצה (מעלים את השעון המסתובב בטלגרם)
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_id})

        if data == "wallet":
            stats = get_user_stats(user_id) # (xp, slh, balance, lang)
            text = f"💰 **הארנק שלך**\n\n💎 SLH: {stats[1]:,}\n⭐ XP: {stats[0]:,}\n💵 יתרה: {stats[2]:,}"
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

        elif data == "games":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id, 
                "text": "🎮 **מרכז המשחקים**\nבקרוב: רולטה, בלקג'ק וכרייה אקטיבית!"
            })

        elif data == "admin_panel":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id, 
                "text": "🛡 **פאנל ניהול אדמין**\nמערכת ה-DB יציבה.\nסטטוס: מחובר כ-Master."
            })
            
    except Exception as e:
        print(f"❌ Callback Error: {e}")