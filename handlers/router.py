import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, BOT_USERNAME, REF_REWARD, PRICE_SH, ZIP_LINK
from buttons.menus import get_main_menu
from db.users import add_user

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    if "photo" in message:
        # טיפול בהוכחת תשלום (נשאר כפי שהיה)
        photo_id = message["photo"][-1]["file_id"]
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": ADMIN_ID,
            "text": f"💰 **הוכחת תשלום חדשה!**\nמאת: {user_id}",
            "reply_markup": {"inline_keyboard": [[{"text": "✅ אשר גישה", "callback_data": f"approve_{user_id}"}]]}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json={"chat_id": ADMIN_ID, "photo": photo_id})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "✅ התמונה התקבלה! המנהל בודק את ההעברה."})
        return

    if text.startswith("/start"):
        add_user(user_id)
        
        welcome_text = (
            f"🏆 **ברוך הבא לנבחרת ה-VIP** 🏆\n\n"
            f"הגעת למקום שבו הופכים ידע לכסף\\.\n\n"
            f"🤝 תוכנית שותפים: **{REF_REWARD}% עמלה**\n"
            f"💰 מחיר הצטרפות: {PRICE_SH}"
        )
        
        menu = get_main_menu("he", user_id)
        
        # אם יש לינק לתמונה במשתנה ZIP_LINK או בערך קבוע - נשתמש בו כבאנר
        banner_url = "https://images.unsplash.com/photo-1611974717535-7c8059622843?q=80&w=1000" # דוגמה לבאנר שוק ההון
        
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json={
            "chat_id": user_id,
            "photo": banner_url,
            "caption": welcome_text,
            "parse_mode": "MarkdownV2",
            "reply_markup": {"inline_keyboard": menu}
        })
