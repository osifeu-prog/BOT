from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests, random, uvicorn, os
from utils.config import TELEGRAM_API_URL, PORT, ADMIN_ID
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db
from db.users import get_user_stats, update_user_balance, get_total_stats

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    initialize_db()
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'bot-production-2668.up.railway.app')}/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}&drop_pending_updates=True")

@app.get("/api/user/{user_id}")
async def get_user_api(user_id: str):
    return {"slh": get_user_stats(user_id)[1]}

@app.post("/api/game-action")
async def game_action(user_id: str, action: str, amount: int):
    # מנוע משחקים אחוד - רולטה, מריו וקזינו
    update_user_balance(user_id, amount)
    return {"status": "success", "new_balance": get_user_stats(user_id)[1]}

@app.get("/api/admin/stats")
async def admin_stats(admin_id: str):
    if admin_id != ADMIN_ID: return {"error": "Unauthorized"}
    return {"stats": get_total_stats()}

@app.get("/", response_class=HTMLResponse)
async def serve_app():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "message" in data: background_tasks.add_task(handle_message, data["message"])
    elif "callback_query" in data: background_tasks.add_task(handle_callback, data["callback_query"])
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)