from fastapi import FastAPI, Request, BackgroundTasks, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import requests
import time
from utils.config import TELEGRAM_API_URL, PORT, ADMIN_ID
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
from db.users import get_user_stats, update_user_balance, get_all_users
import uvicorn

app = FastAPI()
start_time = time.time()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")

# --- ADMIN & MONITORING ENDPOINTS ---

@app.get("/admin/status")
async def get_status(user_id: str = None):
    if user_id != str(ADMIN_ID):
        return {"error": "Unauthorized"}
    
    uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    endpoints = [
        {"path": "/", "desc": "Mini-App Entry"},
        {"path": "/webhook", "desc": "Telegram Entry (POST)"},
        {"path": "/api/user/{id}", "desc": "User Data Sync"},
        {"path": "/api/play", "desc": "Arcade Logic Engine"},
        {"path": "/api/admin/users", "desc": "CRM Database Access"}
    ]
    return {
        "status": "Online",
        "uptime": uptime,
        "total_users": len(get_all_users()),
        "endpoints": endpoints,
        "server_port": PORT
    }

@app.get("/api/admin/users")
async def admin_users_api(user_id: str):
    if user_id != str(ADMIN_ID):
        raise HTTPException(status_code=403)
    users = get_all_users()
    return [{"id": u[0], "name": u[1], "slh": u[2], "ton": u[3]} for u in users]

# --- USER & GAME ENDPOINTS ---

@app.get("/api/user/{user_id}")
async def get_user_api(user_id: str):
    stats = get_user_stats(user_id)
    return {"xp": stats[0], "slh": stats[1], "balance": stats[2]}

@app.post("/api/play")
async def play_game(user_id: str, bet: int):
    import random
    win = random.random() > 0.7
    reward = bet * 4 if win else -bet
    update_user_balance(user_id, reward)
    return {"win": win, "reward": reward, "new_balance": get_user_stats(user_id)[1]}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Dashboard Loading...</h1>"

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    elif "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, workers=1)