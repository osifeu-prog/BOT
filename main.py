import uvicorn
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from utils.config import WEBHOOK_URL, TELEGRAM_API_URL
from utils.logger import logger

app = FastAPI()

def set_bot_commands():
    commands = [
        {"command": "start", "description": "🚀 התחלת עבודה ורענון"},
        {"command": "admin", "description": "🛠 פאנל ניהול (לאדמין בלבד)"}
    ]
    requests.post(f"{TELEGRAM_API_URL}/setMyCommands", json={"commands": commands})

@app.on_event("startup")
async def startup_event():
    init_tables()
    set_bot_commands()
    if WEBHOOK_URL:
        webhook_path = f"{WEBHOOK_URL}/webhook"
        requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_path}&drop_pending_updates=True")
        logger.info("💎 Diamond Bot UI/UX Optimized")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    elif "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    return {"status": "ok"}
