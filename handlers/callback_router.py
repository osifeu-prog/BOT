import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, TON_WALLET, PRICE_SH, VIP_GROUP
from db.slots import play_slots

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    # ביטול השעון המסתובב בטלגרם
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_slots":
        await play_slots(user_id)
    
    elif data == "menu_buy":
        msg = f"💳 **פרטי תשלום להצטרפות**\n\nשלח {PRICE_SH} לכתובת ה-TON הבאה:\n\n{TON_WALLET}\n\n⚠️ **חשוב:** לאחר השליחה, צלם מסך ושלח אותו כאן בצא'ט."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif data.startswith("approve_"):
        target_id = data.split("_")[1]
        # הודעה למשתמש שהגישה נפתחה + לינק לקבוצה מה-Railway
        success_msg = f"🎊 **מזל טוב! הגישה שלך אושרה!**\n\nהנה הלינק לקבוצת ה-VIP הסודית:\n{VIP_GROUP}\n\nבהצלחה במסחר!"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": target_id, "text": success_msg})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": ADMIN_ID, "text": f"✅ המשתמש {target_id} אושר וקיבל לינק לקבוצה."})
