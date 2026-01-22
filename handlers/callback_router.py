import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET, ADMIN_USERNAME
from db.users import get_user_stats, get_leaderboard

async def handle_callback(callback_query):
    try:
        user_id = str(callback_query.get("from", {}).get("id"))
        data = callback_query.get("data", "")
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})

        if data == "buy_bot":
            text = (
                "🚀 **רכישת מערכת Diamond VIP לעסק**\n\n"
                "החבילה כוללת:\n"
                "• בוט טלגרם מעוצב\n"
                "• Mini-App (ארקייד/Dashboard)\n"
                "• מערכת ארנק ו-AI מובנית\n\n"
                "💳 **עלות: 500 TON**\n\n"
                "להעברת תשלום ורכישה מיידית, השתמש בכפתור למטה:"
            )
            keyboard = [[{"text": "💳 בצע תשלום (TON)", "callback_data": "payment_info"}],
                        [{"text": "💬 פנה לאדמין בפרטי", "url": f"https://t.me/{ADMIN_USERNAME}"}]]
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id, "text": text, "reply_markup": {"inline_keyboard": keyboard}, "parse_mode": "Markdown"
            })

        elif data == "payment_info":
            text = f"⚠️ **העברת תשלום עבור רכישת בוט**\n\nכתובת ארנק TON:\n{TON_WALLET}\n\nלאחר ההעברה, שלח צילום מסך ל-@{ADMIN_USERNAME} להפעלת המערכת."
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

        elif data == "ai_chat":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 המוח של ה-AI מתחבר כעת... (בקרוב תוכל לשלוח שאלות ישירות כאן)"})

        elif data == "settings":
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "⚙️ **הגדרות מערכת**\n\n• שפה: עברית\n• התראות: פעיל\n• זיהוי ביומטרי: מופעל"})

        elif data == "wallet":
            stats = get_user_stats(user_id)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"💰 **ארנק**\n💎 SLH: {stats[1]}\n💵 יתרה: {stats[2]}"})

        elif data == "leaderboard":
            leaders = get_leaderboard()
            text = "🏆 **מובילים**\n" + "\n".join([f"{i}. {u}: {s}" for i, (u, s) in enumerate(leaders, 1)])
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

    except Exception as e:
        print(f"❌ Callback Error: {e}")