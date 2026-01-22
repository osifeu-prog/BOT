import os
import uvicorn
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.init_db import init_tables
from utils.config import WEBHOOK_URL, TELEGRAM_BOT_TOKEN

app = FastAPI()

@app.on_event("startup")
async def startup_db():
    init_tables()
    if WEBHOOK_URL:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook"
        requests.get(url)
        print(f"Webhook set: {WEBHOOK_URL}")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    elif "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
