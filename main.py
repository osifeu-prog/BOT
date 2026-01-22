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
processed_updates = set()

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = "https://bot-production-2668.up.railway.app/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Diamond VIP Arcade</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: radial-gradient(circle, #1a1a2e 0%, #07070a 100%); color: white; text-align: center; margin: 0; padding: 20px; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden; }
            .diamond { font-size: 100px; margin-bottom: 20px; filter: drop-shadow(0 0 30px #00d2ff); animation: float 3s ease-in-out infinite; }
            h1 { color: #00d2ff; text-transform: uppercase; letter-spacing: 3px; text-shadow: 0 0 15px #00d2ff; margin: 10px 0; font-size: 28px; }
            .status-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 25px; padding: 25px; width: 85%; backdrop-filter: blur(15px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            .user-welcome { font-size: 20px; margin-bottom: 10px; color: #fff; }
            .sync-text { color: #00ff88; font-weight: bold; font-size: 14px; text-transform: uppercase; }
            .btn-close { margin-top: 30px; background: linear-gradient(45deg, #00d2ff, #3a7bd5); border: none; padding: 12px 40px; color: white; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 20px rgba(0, 210, 255, 0.4); }
            @keyframes float { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-20px) rotate(5deg); } }
        </style>
    </head>
    <body>
        <div class="diamond">💎</div>
        <h1>Diamond VIP Arcade</h1>
        <div class="status-card">
            <div class="user-welcome">שלום, <span id="user-name">VIP User</span>!</div>
            <div class="sync-text">● המערכת מחוברת ומסונכרנת</div>
        </div>
        <button class="btn-close" onclick="window.Telegram.WebApp.close()">סגור וחזור לבוט</button>
        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                document.getElementById('user-name').innerText = tg.initDataUnsafe.user.first_name;
            }
        </script>
    </body>
    </html>
    """

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    update_id = data.get("update_id")
    if update_id in processed_updates: return {"ok": True}
    processed_updates.add(update_id)
    if len(processed_updates) > 500: processed_updates.clear()

    if "message" in data:
        background_tasks.add_task(handle_message, data["message"])
    elif "callback_query" in data:
        background_tasks.add_task(handle_callback, data["callback_query"])
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, workers=1)