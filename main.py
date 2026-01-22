from fastapi import FastAPI, Request
import requests
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")
    print("🚀 Server Started & Webhook Synced")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    # טיפול בהודעות טקסט
    if "message" in data:
        await handle_message(data["message"])
    
    # טיפול בלחיצות על כפתורים
    elif "callback_query" in data:
        await handle_callback(data["callback_query"])
        
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)