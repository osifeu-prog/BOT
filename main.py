import uvicorn
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from utils.config import WEBHOOK_URL, TELEGRAM_TOKEN, TELEGRAM_API_URL, DATABASE_URL, REDIS_URL
from utils.logger import logger
import psycopg2

app = FastAPI()

@app.on_event("startup")
async def startup_check():
    # בדיקת Postgres
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        logger.info("✅ Database (PostgreSQL): Connected")
    except Exception as e:
        logger.error(f"❌ Database Connection Failed: {e}")

    # בדיקת Webhook
    if WEBHOOK_URL:
        webhook_path = f"{WEBHOOK_URL}/webhook"
        requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_path}&drop_pending_updates=True")
        logger.info(f"🚀 Webhook set to: {webhook_path}")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    elif "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    return {"status": "ok"}
