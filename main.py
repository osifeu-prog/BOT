import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from db.upgrade import upgrade_tables
from utils.config import WEBHOOK_URL, TELEGRAM_API_URL
from utils.logger import logger

app = FastAPI()

@app.on_event("startup")
async def startup():
    init_tables()
    upgrade_tables()
    if WEBHOOK_URL:
        requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/webhook&drop_pending_updates=True")
        logger.info("🚀 System Online & Upgraded")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    elif "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    return {"status": "ok"}
