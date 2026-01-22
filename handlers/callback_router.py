import requests, random
from utils.config import TELEGRAM_API_URL, ADMIN_ID, BOT_USERNAME
from db.connection import get_conn

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "menu_rank":
        # שליפת טבלת מובילים מה-Postgres
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        leaderboard = "🏆 **טבלת מובילים - VIP** 🏆\n\n"
        for i, row in enumerate(rows):
            leaderboard += f"{i+1}. ID: {row[0]} - {row[1]}\n"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": leaderboard, "parse_mode": "Markdown"})

    elif data == "menu_wheel":
        # משחק קוביות עם אנימציה של טלגרם
        res = requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": "🎲"}).json()
        value = res["result"]["dice"]["value"]
        msg = f"הקוביה נעצרה על: {value}! "
        msg += "זכית בבונוס!" if value >= 5 else "כמעט! נסה שוב."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif data == "menu_slots":
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": "🎰"})
