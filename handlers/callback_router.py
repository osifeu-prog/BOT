import requests, random
from utils.config import TELEGRAM_API_URL, ADMIN_ID, TON_WALLET, PRICE_SH, VIP_LINK
from db.connection import get_conn

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    # אישור קבלת לחיצה
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_rank":
        # משיכת טבלת מובילים מה-Postgres
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        text = "🏆 **מובילי השבוע בנבחרת** 🏆\n\n"
        for i, row in enumerate(rows):
            text += f"{i+1}# • ID: {row[0]} — *{row[1]}*\n"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": text, "parse_mode": "Markdown"})

    elif data == "menu_wheel":
        # קוביות טלגרם (אנימציית קצה)
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": "🎲"})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🎯 **הקוביות הוטלו!** אם יצא 6 - תקבל קופון הנחה בפרטי!"})

    elif data == "menu_slots":
        # אנימציית סלוטס אמיתית של טלגרם
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": "🎰"})
