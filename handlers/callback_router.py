import requests
from utils.config import TELEGRAM_API_URL, ADMIN_USERNAME, TOKEN_PACKS, PRICE_SH, TON_WALLET

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_main":
        from handlers.router import handle_message
        await handle_message({"from": {"id": user_id}, "text": "/start"})

    elif data == "menu_games":
        from buttons.menus import get_games_menu
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 **קזינו ה-VIP:**",
            "reply_markup": {"inline_keyboard": get_games_menu()}
        })

    elif data.startswith("game_"):
        emoji_map = {"game_slots": "🎰", "game_dice": "🎲", "game_dart": "🎯", "game_hoop": "🏀", "game_bowling": "🎳"}
        emoji = emoji_map.get(data, "🎲")
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": emoji})

    elif data == "menu_tokens":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": f"💎 **חבילות:**\n\n{TOKEN_PACKS}"})

    elif data == "buy_bot":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": f"🤖 לפרטים על רכישת מערכת: @{ADMIN_USERNAME}"
        })

    elif data == "menu_courses":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": f"📚 מסלול VIP: {PRICE_SH}\nארנק: {TON_WALLET}", "parse_mode": "Markdown"
        })
