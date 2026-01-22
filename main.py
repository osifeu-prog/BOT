from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import asyncio
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
import uvicorn

app = FastAPI()

# מנגנון זיכרון גלובלי למניעת כפילויות
processed_updates = set()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")
    print("🚀 System Stabilized & Mini-App Route Active")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return "<html><body><h1>Diamond VIP Arcade</h1><p>Welcome to the Mini-App!</p></body></html>"

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update_id = data.get("update_id")
    
    if not update_id or update_id in processed_updates:
        return {"status": "ignored"}
    
    processed_updates.add(update_id)
    if len(processed_updates) > 200:
        processed_updates.clear() # איפוס מבוקר

    if "message" in data:
        await handle_message(data["message"])
    elif "callback_query" in data:
        await handle_callback(data["callback_query"])
        
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)