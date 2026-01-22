from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests, os, uvicorn
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message, handle_callback
from db.connection import initialize_db

app = FastAPI()

# וידוא תיקיות
if not os.path.exists("templates"): os.makedirs("templates")

@app.on_event("startup")
async def startup():
    initialize_db()
    # הגדרת Webhook אוטומטית
    url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'bot-production-2668.up.railway.app')}/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={url}")

@app.get("/")
async def home(request: Request):
    from fastapi.responses import HTMLResponse
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/user/{user_id}")
async def get_user_api(user_id: str):
    from db.users import get_user_stats
    stats = get_user_stats(user_id)
    return {"slh": stats[1], "rank": stats[2] if len(stats)>2 else "Starter"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if "message" in data:
        handle_message(data["message"])
    elif "callback_query" in data:
        handle_callback(data["callback_query"])
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
