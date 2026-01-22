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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Diamond VIP Arcade</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            :root { --glow-color: #00d2ff; --bg-dark: #05050a; }
            body { font-family: 'Segoe UI', system-ui; background: var(--bg-dark); color: white; margin: 0; padding: 0; overflow-x: hidden; }
            .hero { height: 250px; background: linear-gradient(180deg, #1a1a2e 0%, var(--bg-dark) 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
            .diamond { font-size: 80px; filter: drop-shadow(0 0 20px var(--glow-color)); animation: float 3s ease-in-out infinite; }
            h1 { font-size: 26px; letter-spacing: 5px; color: var(--glow-color); text-shadow: 0 0 10px var(--glow-color); margin: 10px 0; }
            .arcade-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 20px; }
            .game-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 15px; padding: 20px; text-align: center; backdrop-filter: blur(5px); transition: 0.3s; }
            .game-card:active { transform: scale(0.95); border-color: var(--glow-color); }
            .game-icon { font-size: 40px; margin-bottom: 10px; }
            .game-title { font-weight: bold; font-size: 14px; color: #ddd; }
            .footer-nav { position: fixed; bottom: 0; width: 100%; background: rgba(26, 26, 46, 0.95); padding: 15px 0; border-top: 1px solid var(--glow-color); text-align: center; }
            .buy-btn { background: linear-gradient(45deg, #00d2ff, #3a7bd5); border: none; padding: 12px 30px; color: white; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0 0 15px var(--glow-color); }
            @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="diamond">💎</div>
            <h1>DIAMOND ARCADE</h1>
            <p style="color: #888; font-size: 12px;">מחובר כעת: <span id="user-name" style="color:var(--glow-color)">VIP</span></p>
        </div>
        
        <div class="arcade-grid">
            <div class="game-card">
                <div class="game-icon">🎰</div>
                <div class="game-title">סלוט יהלום</div>
                <div style="font-size:10px; color: #00ff88;">פעיל</div>
            </div>
            <div class="game-card">
                <div class="game-icon">🃏</div>
                <div class="game-title">פוקר AI</div>
                <div style="font-size:10px; color: #ffaa00;">בקרוב</div>
            </div>
            <div class="game-card">
                <div class="game-icon">🚀</div>
                <div class="game-title">קראש מטבעות</div>
                <div style="font-size:10px; color: #ffaa00;">בקרוב</div>
            </div>
            <div class="game-card">
                <div class="game-icon">🔮</div>
                <div class="game-title">גלגל המזל</div>
                <div style="font-size:10px; color: #00ff88;">פעיל</div>
            </div>
        </div>

        <div style="padding: 20px; margin-bottom: 100px;">
            <div style="background: rgba(0, 210, 255, 0.1); border-radius: 10px; padding: 15px; border-right: 4px solid var(--glow-color);">
                <div style="font-weight: bold;">מעוניין בבוט כזה לעסק שלך?</div>
                <div style="font-size: 12px; margin-top: 5px; color: #ccc;">כרטיס ביקור דיגיטלי הכולל מיני-אפ, ארנק וניהול לקוחות.</div>
            </div>
        </div>

        <div class="footer-nav">
            <button class="buy-btn" onclick="tg.close()">לרכישת המערכת ופרטים</button>
        </div>

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