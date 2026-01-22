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
    # מחיקה אקטיבית של הודעות ישנות
    requests.get(f"{TELEGRAM_API_URL}/deleteWebhook?drop_pending_updates=True")
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")
    print("🚀 System Cleaned & Online")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        await handle_message(data["message"])
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)