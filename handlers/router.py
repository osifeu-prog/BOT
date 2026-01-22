import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, BOT_USERNAME, REF_REWARD, PRICE_SH
from buttons.menus import get_main_menu
from db.users import add_user

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    if "photo" in message:
        photo_id = message["photo"][-1]["file_id"]
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": ADMIN_ID,
            "text": f"💰 **הוכחת תשלום חדשה!**\nID: {user_id}",
            "reply_markup": {"inline_keyboard": [[{"text": "✅ אשר גישה", "callback_data": f"approve_{user_id}"}]]}
        })
        return

    if text.startswith("/start"):
        add_user(user_id)
        msg = f"🏆 **VIP TRADING BOT** 🏆\n\nברוך הבא למערכת המסחר המתקדמת ביותר\\.\n\n💰 מחיר קורס: {PRICE_SH}\n🤝 עמלת שותף: {REF_REWARD}%"
        menu = get_main_menu("he", user_id)
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": msg, 
            "parse_mode": "MarkdownV2", 
            "reply_markup": {"inline_keyboard": menu}
        })
