from fastapi import FastAPI, Request, BackgroundTasks
import requests, os, uvicorn
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message, handle_callback
from db.connection import initialize_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    initialize_db()

@app.get("/")
async def home():
    return {"status": "Mini-App Server is Up"}

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
