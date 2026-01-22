import requests
from utils.config import TELEGRAM_API_URL, TON_WALLET, PRICE_SH, TOKEN_PACKS, VIP_GROUP, LESSON_PRICE, ADMIN_USERNAME

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_tokens":
        msg = f"💎 **חבילות טוקנים זמינות:**\n\n{TOKEN_PACKS}\n\nלבחירת חבילה ורכישה, פנה למנהל: @{ADMIN_USERNAME}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "menu_courses":
        from buttons.menus import get_courses_menu
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "📚 **בחר את מסלול הלמידה שלך:**",
            "reply_markup": {"inline_keyboard": get_courses_menu()}
        })

    elif data == "buy_vip":
        msg = f"💳 **רכישת גישת VIP מלאה**\n\nשלח {PRICE_SH} לכתובת:\n{TON_WALLET}\n\nלאחר מכן שלח צילום מסך כאן."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "buy_bot":
        msg = f"🤖 **רוצה בוט כזה לעסק שלך?**\n\nהמערכת שלנו כוללת:\n• ניהול שותפים\n• סליקת קריפטו\n• משחקי מזל\n\nלפרטים ומחירים פנה אלינו: @{ADMIN_USERNAME}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif data == "menu_main":
        from handlers.router import send_start_msg
        await send_start_msg(user_id)
