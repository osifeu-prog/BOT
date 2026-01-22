from fastapi import FastAPI, Request
import requests
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
import uvicorn, os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    
    # שימוש בכתובת המדויקת של Railway
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    
    print(f"📡 Setting Webhook to: {webhook_url}")
    set_resp = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True").json()
    print(f"📡 Telegram Response: {set_resp}")
    
    # בדיקה אם ה-Webhook הוגדר בהצלחה
    info = requests.get(f"{TELEGRAM_API_URL}/getWebhookInfo").json()
    print(f"🔍 Current Webhook Info: {info}")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        await handle_message(data["message"])
    elif "callback_query" in data:
        await handle_callback(data["callback_query"])
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"status": "Active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)