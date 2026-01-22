import uvicorn
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from utils.config import WEBHOOK_URL, TELEGRAM_TOKEN, TELEGRAM_API_URL
from utils.logger import logger

app = FastAPI()

@app.on_event("startup")
async def startup_db():
    init_tables()
    if WEBHOOK_URL:
        # בייצור - לא מוחקים הודעות שמחכות (drop_pending_updates=False)
        webhook_path = f"{WEBHOOK_URL}/webhook"
        requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_path}&drop_pending_updates=False")
        logger.info("🚀 Production Webhook Active")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        if "callback_query" in data:
            background_tasks.add_task(handle_callback, data["callback_query"])
        elif "message" in data:
            background_tasks.add_task(handle_message, data["message"])
    except Exception as e:
        logger.error(f"⚠️ Webhook processing error: {e}")
    return {"status": "ok"}
