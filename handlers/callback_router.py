import requests, random, asyncio
from utils.config import TELEGRAM_API_URL, ADMIN_ID, TON_WALLET, PRICE_SH, BOT_USERNAME, REF_REWARD
from db.slots import play_slots

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_main":
        from handlers.router import send_start_msg
        send_start_msg(user_id)

    elif data == "menu_games":
        from buttons.menus import get_games_menu
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "🎮 **מתחם המשחקים והפרסים**\nבחר משחק ונסה לזכות בהנחה לקורס!",
            "reply_markup": {"inline_keyboard": get_games_menu()}
        })

    elif data == "menu_affiliate":
        share_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        msg = (
            "🤝 **מרכז השותפים של ה-VIP**\n\n"
            f"שתף את הלינק שלך וקבל **{REF_REWARD}%** עמלה על כל רכישה\\!\n\n"
            f"🔗 הלינק האישי שלך:\n{share_link}\n\n"
            "💰 *הכסף נשלח אוטומטית לארנק שלך לאחר אישור המכירה\\.*"
        )
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "MarkdownV2"})

    elif data == "menu_tools":
        msg = "🧮 **מחשבון ניהול סיכונים (Risk/Reward)**\n\nבקרוב: שלח לבוט את גודל התיק והוא יחשב לך את גודל הפוזיציה המומלץ."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif data == "menu_slots":
        await play_slots(user_id)

    elif data == "menu_buy":
        banner = "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?q=80&w=1000"
        msg = f"💎 **הצטרפות למסלול המהיר**\n\nמחיר: {PRICE_SH}\nכתובת (TON):\n{TON_WALLET}\n\nצלם מסך ושלח לכאן בסיום."
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json={"chat_id": user_id, "photo": banner, "caption": msg, "parse_mode": "Markdown"})
