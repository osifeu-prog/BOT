from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
import requests
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

# דף הבית של המיני-אפ - עיצוב Diamond VIP משודרג
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
            body { font-family: sans-serif; background: radial-gradient(circle, #1a1a2e 0%, #0f0f1b 100%); color: white; text-align: center; margin: 0; padding: 20px; overflow: hidden; }
            .diamond { font-size: 80px; margin-top: 50px; filter: drop-shadow(0 0 20px #00d2ff); animation: float 3s ease-in-out infinite; }
            h1 { color: #00d2ff; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px #00d2ff; }
            .card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 20px; padding: 20px; margin: 20px auto; max-width: 90%; backdrop-filter: blur(10px); }
            .btn { background: linear-gradient(45deg, #00d2ff, #3a7bd5); border: none; padding: 15px 30px; color: white; border-radius: 50px; font-weight: bold; cursor: pointer; transition: 0.3s; box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4); }
            .btn:active { transform: scale(0.95); }
            @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
        </style>
    </head>
    <body>
        <div class="diamond">💎</div>
        <h1>Diamond VIP Arcade</h1>
        <div class="card">
            <p>ברוך הבא, <span id="user-name">אורח</span>!</p>
            <p>היתרה שלך בסנכרון...</p>
        </div>
        <button class="btn" onclick="tg.close()">חזרה לבוט</button>
        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();
            document.getElementById('user-name').innerText = tg.initDataUnsafe.user ? tg.initDataUnsafe.user.first_name : 'VIP User';
        </script>
    </body>
    </html>
    """

async def process_update(data):
    if "message" in data:
        await handle_message(data["message"])
    elif "callback_query" in data:
        await handle_callback(data["callback_query"])

@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    update_id = data.get("update_id")
    
    if update_id in processed_updates:
        return {"ok": True}
    
    processed_updates.add(update_id)
    if len(processed_updates) > 500: processed_updates.clear()

    # שליחה לעיבוד ברקע כדי לענות לטלגרם מיד ב-200 OK
    background_tasks.add_task(process_update, data)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)