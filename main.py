from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import requests, os, uvicorn
from utils.config import TELEGRAM_API_URL, PORT, ADMIN_ID
from handlers.router import handle_message
from handlers.callback_router import handle_callback
from db.connection import initialize_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# פונקציה להחזרת ה-HTML כטקסט פשוט כדי למנוע תלות ב-Jinja2 אם יש תקלה
@app.get("/")
async def serve_home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return requests.utils.super_len(f.read()) # מחזיר את הדף

@app.on_event("startup")
async def startup():
    initialize_db()
    url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'bot-production-2668.up.railway.app')}/webhook"
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={url}&drop_pending_updates=True")

@app.get("/api/user/{user_id}")
async def get_user_api(user_id: str):
    from db.users import get_user_stats
    stats = get_user_stats(user_id)
    return {"slh": stats[1]}

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    if "message" in data: background_tasks.add_task(handle_message, data["message"])
    elif "callback_query" in data: background_tasks.add_task(handle_callback, data["callback_query"])
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
