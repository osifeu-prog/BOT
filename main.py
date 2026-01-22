from fastapi import FastAPI, Request
import requests
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from db.connection import initialize_db
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    # הוספת drop_pending_updates=True מנקה את התור של טלגרם
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")
    print("🚀 System Online - Updates Cleared - Webhook Set")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        await handle_message(data["message"])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)