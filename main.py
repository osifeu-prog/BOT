import os
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.events import log_event
from utils.config import WEBHOOK_URL, TELEGRAM_TOKEN, TELEGRAM_API_URL
import requests

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is running", "mode": "Production"}

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        
        if "message" in data:
            background_tasks.add_task(handle_message, data["message"])
        elif "callback_query" in data:
            background_tasks.add_task(handle_callback, data["callback_query"])
            
        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing update: {e}")
        return {"status": "error", "message": str(e)}

# אתחול ה-Webhook בטיחותי
@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/webhook"
        requests.get(url)
        print(f"Webhook set to: {WEBHOOK_URL}/webhook")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
