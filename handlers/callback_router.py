import requests
from utils.config import TELEGRAM_API_URL
from buttons.menus import get_games_menu
from db.users import update_user_economy

async def handle_callback(callback_query):
    user_id = str(callback_query["from"]["id"])
    data = callback_query.get("data", "")
    chat_id = callback_query["message"]["chat"]["id"]
    msg_id = callback_query["message"]["message_id"]

    if data == "open_games":
        requests.post(f"{TELEGRAM_API_URL}/editMessageText", json={
            "chat_id": chat_id, "message_id": msg_id,
            "text": "🎮 **Arcade VIP**\nשחק וצבור מטבעות SLH:",
            "reply_markup": {"inline_keyboard": get_games_menu('he')}
        })
    elif data == "play_dice":
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"})
        update_user_economy(user_id, xp_add=5)
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})