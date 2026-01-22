from utils.telegram import send_message
from db.slots import play_slots
from utils.config import PRICE_SH, TON_WALLET, ADMIN_ID, TELEGRAM_API_URL
import requests

async def menu_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    callback_id = callback["id"]
    
    # שליחת התראה קופצת בתוך טלגרם (Toast)
    def notify(text):
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={
            "callback_query_id": callback_id,
            "text": text,
            "show_alert": False
        })

    if data == "menu_slots":
        notify("🎰 המכונה נכנסת לפעולה...")
        await play_slots(user_id)
        
    elif data == "menu_buy":
        notify("💳 מכין פרטי תשלום...")
        msg = f"✨ **פרטי העברה** ✨\n\nסכום: {PRICE_SH}\nכתובת (TON):\n{TON_WALLET}\n\nאנא שלח צילום מסך של ההעברה לכאן."
        send_message(user_id, msg, {"inline_keyboard": [[{"text": "✅ שלחתי - בקש אישור", "callback_data": "req_approve"}]]})

    elif data == "req_approve":
        notify("📧 בקשה נשלחה!")
        admin_msg = f"💰 **משתמש מחכה לאישור!**\nID: {user_id}\nשם: {callback['from'].get('first_name')}"
        send_message(ADMIN_ID, admin_msg, {"inline_keyboard": [[{"text": "✅ אשר גישה", "callback_data": f"approve_{user_id}"}]]})
        send_message(user_id, "⏳ המנהל קיבל את הבקשה. מיד תקבל הודעה.")

    elif data.startswith("approve_"):
        uid = data.split("_")[1]
        notify("✅ בוצע!")
        send_message(uid, "🎊 **מזל טוב! הגישה שלך לקורס נפתחה!**\nלחץ /start כדי להתחיל ללמוד.")
        send_message(ADMIN_ID, f"בוצע! משתמש {uid} הוגדר כרוכש.")
