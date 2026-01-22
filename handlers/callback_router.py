import requests
from utils.config import TELEGRAM_API_URL, BOT_USERNAME

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    # אישור קבלת הלחיצה
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_main":
        from handlers.router import handle_message
        await handle_message({"from": {"id": user_id}, "text": "/start"})

    elif data == "menu_games":
        from buttons.menus import get_games_menu
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 **קזינו ה-VIP זמין!**\nבחר משחק והרווח SLH:",
            "reply_markup": {"inline_keyboard": get_games_menu()}
        })

    elif data.startswith("game_"):
        emoji_map = {"game_slots": "🎰", "game_dice": "🎲", "game_dart": "🎯", "game_hoop": "🏀", "game_bowling": "🎳"}
        emoji = emoji_map.get(data, "🎲")
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": emoji})

    elif data == "menu_affiliate":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        msg = f"🤝 **תוכנית השותפים:**\nשלח את הלינק לחברים וקבל 100 SLH על כל מצטרף!\n\n{ref_link}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})
