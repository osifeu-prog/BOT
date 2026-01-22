import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, BOT_USERNAME, REF_REWARD, PRICE_SH, ZIP_LINK
from buttons.menus import get_main_menu
from db.users import add_user

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    if "photo" in message:
        photo_id = message["photo"][-1]["file_id"]
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": ADMIN_ID,
            "text": f"💰 **הוכחת תשלום חדשה!**\nמאת: {user_id}",
            "reply_markup": {"inline_keyboard": [[{"text": "✅ אשר גישה", "callback_data": f"approve_{user_id}"}]]}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json={"chat_id": ADMIN_ID, "photo": photo_id})
        return

    if text.startswith("/start"):
        add_user(user_id)
        welcome_text = (
            f"🏆 *WELCOME TO THE VIP CIRCLE* 🏆\n\n"
            f"הגעת למקום הנכון למסחר מקצועי\\.\n\n"
            f"🤝 תוכנית שותפים: *{REF_REWARD}% עמלה*\n"
            f"💰 מחיר הצטרפות: {PRICE_SH}"
        )
        
        menu = get_main_menu("he", user_id)
        
        # שליחת התמונה (באנר)
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json={
            "chat_id": user_id,
            "photo": ZIP_LINK,
            "caption": welcome_text,
            "parse_mode": "MarkdownV2",
            "reply_markup": {"inline_keyboard": menu}
        })
