from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
import requests
import asyncio
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
import uvicorn

app = FastAPI()
processed_updates = {}

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    # איפוס מוחלט של ה-Webhook בטלגרם
    requests.get(f"{TELEGRAM_API_URL}/deleteWebhook?drop_pending_updates=True")
    await asyncio.sleep(2)
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return "<html><body style='background:#0f0f1b;color:white;text-align:center;'><h1>Diamond VIP Arcade</h1></body></html>"

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    update_id = data.get("update_id")
    
    # מניעת כפילות מוחלטת
    if update_id in processed_updates:
        return {"ok": True}
    processed_updates[update_id] = True
    
    background_tasks.add_task(handle_message if "message" in data else handle_callback, data.get("message") or data.get("callback_query"))
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, workers=1)