from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
import requests, time, random, uvicorn, os
from utils.config import TELEGRAM_API_URL, PORT, ADMIN_ID
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
from db.users import get_user_stats, update_user_balance, get_all_users

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    # חיבור מחדש של הבוט לשרת - זה משחרר את ה"חסימה"
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")

@app.get("/api/user/{user_id}")
async def get_user_api(user_id: str):
    stats = get_user_stats(user_id)
    return {"slh": stats[1]}

@app.post("/api/play")
async def play_game(user_id: str, bet: int):
    # מנוע משחק משופר
    win = random.random() < 0.3 # 30% סיכוי זכייה כברירת מחדל
    reward = bet * 2 if win else -bet
    update_user_balance(user_id, reward)
    stats = get_user_stats(user_id)
    return {"win": win, "reward": reward, "new_balance": stats[1]}

@app.post("/api/daily-spin")
async def daily_spin(user_id: str):
    prizes = [0, 10, 20, 50, 0, 100, 0, 5]
    win_amount = random.choice(prizes)
    update_user_balance(user_id, win_amount)
    stats = get_user_stats(user_id)
    return {"win": win_amount > 0, "amount": win_amount, "new_balance": stats[1]}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "message" in data: 
        background_tasks.add_task(handle_message, data["message"])
    elif "callback_query" in data: 
        background_tasks.add_task(handle_callback, data["callback_query"])
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)