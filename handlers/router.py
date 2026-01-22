import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, PRICE_SH
from buttons.menus import get_main_menu
from db.users import add_user
from utils.logger import logger

async def handle_message(message):
    try:
        user_id = message["from"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/start"):
            add_user(user_id)
            msg = f"🏆 **VIP TRADING BOT**\n\nהמערכת פעילה ומחכה לך.\n\n💰 עלות כניסה: {PRICE_SH}"
            menu = get_main_menu("he", user_id)
            
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": user_id, 
                "text": msg,
                "reply_markup": {"inline_keyboard": menu}
            })
            logger.info(f"✅ Start sent to {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Error in handle_message: {e}")
