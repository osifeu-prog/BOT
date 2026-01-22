import os
import uvicorn
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from utils.config import WEBHOOK_URL, TELEGRAM_TOKEN, TELEGRAM_API_URL

app = FastAPI()

@app.on_event("startup")
async def startup_db():
    init_tables()
    if WEBHOOK_URL:
        # עדכון ה-Webhook מול טלגרם
        requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/webhook")

@app.get("/")
async def health_check():
    return {"status": "online", "mode": "Diamond-Edition"}

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    elif "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    return {"status": "ok"}
