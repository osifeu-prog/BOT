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
        webhook_path = f"{WEBHOOK_URL}/webhook"
        print(f"📡 Setting Webhook to: {webhook_path}")
        # מחיקת וובהוק ישן והגדרה מחדש
        requests.get(f"{TELEGRAM_API_URL}/deleteWebhook?drop_pending_updates=True")
        r = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_path}")
        print(f"🛠 Webhook Status: {r.json()}")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print(f"📩 Incoming Data: {data}") # זה יראה לנו בלוגים מה קורה
    
    if "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    elif "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    return {"status": "ok"}

@app.get("/")
async def health():
    return {"status": "up"}
