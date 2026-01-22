import requests
from utils.config import TELEGRAM_API_URL
from buttons.menus import get_games_menu

async def handle_callback(callback_query):
    user_id = str(callback_query["from"]["id"])
    data = callback_query.get("data", "")
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]

    if data == "open_games":
        requests.post(f"{TELEGRAM_API_URL}/editMessageText", json={
            "chat_id": chat_id, "message_id": message_id,
            "text": "🎮 **מרכז המשחקים**\nבחר משחק וצבור SLH:",
            "reply_markup": {"inline_keyboard": get_games_menu('he')}
        })
    
    elif data == "open_courses":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": "📚 **האקדמיה ל-VIP**\nהקורסים שלך בדרך..."
        })
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})