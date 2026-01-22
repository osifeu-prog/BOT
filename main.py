from fastapi import FastAPI, Request
import requests
import asyncio
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
import uvicorn

app = FastAPI()

# משתנה למניעת עיבוד כפול של אותה הודעה בשניות קרובות
processed_updates = set()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    # ניקוי מוחלט של כל ההודעות שמחכות בשרת טלגרם
    requests.get(f"{TELEGRAM_API_URL}/deleteWebhook?drop_pending_updates=True")
    await asyncio.sleep(1) # הפסקה קצרה לסנכרון
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")
    print("🛡️ System Locked & Stabilized - No More Duplicate Messages")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update_id = data.get("update_id")
    
    # הגנה מפני עיבוד כפול של אותו Update
    if update_id in processed_updates:
        return {"status": "already_processed"}
    processed_updates.add(update_id)
    if len(processed_updates) > 100: # ניקוי הזיכרון מדי פעם
        processed_updates.pop()

    if "message" in data:
        await handle_message(data["message"])
    elif "callback_query" in data:
        await handle_callback(data["callback_query"])
        
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)