import os
import uvicorn
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from utils.config import WEBHOOK_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL

app = FastAPI()

@app.on_event("startup")
async def startup_db():
    init_tables()
    if WEBHOOK_URL:
        requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/webhook")

@app.get("/")
async def health_check():
    return {"status": "online", "version": "3.0.0-Premium", "service": "Payment Bot"}

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # אישור קבלת לחיצה (מונע מהשעון על הכפתור להמשיך להסתובב)
    if "callback_query" in data:
        callback = data["callback_query"]
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
        background_tasks.add_task(handle_callback, callback)
    
    # טיפול בהודעות טקסט או תמונות
    elif "message" in data:
        background_tasks.add_task(handle_message, data["message"])
        
    return {"status": "ok"}
