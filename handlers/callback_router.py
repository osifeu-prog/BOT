import requests
from utils.config import TELEGRAM_API_URL, ADMIN_USERNAME, TOKEN_PACKS, PRICE_SH, TON_WALLET

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    # שליחת אישור קבלת לחיצה (חשוב מאוד!)
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_tokens":
        msg = f"💎 **חבילות טוקנים:**\n\n{TOKEN_PACKS}\n\nלרכישה פנה למנהל: @{ADMIN_USERNAME}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "menu_courses":
        msg = f"📚 **מסלולי VIP**\n\nמסלול מלא: {PRICE_SH}\n\nלתשלום שלח לקנק: {TON_WALLET}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "menu_games":
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": "🎰"})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🎰 **מכונת המזל הופעלה!**"})

    elif data == "buy_bot":
        msg = "🤖 **רוצה מערכת כזו משלך?**\n\nהמערכת כוללת פאנל ניהול, סליקה אוטומטית ומערכת שותפים.\n\nצור קשר: @{ADMIN_USERNAME}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})
