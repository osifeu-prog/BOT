"""
main.py
========
HE: קובץ הכניסה הראשי של הבוט — FastAPI + Webhook.
EN: Main entry point of the bot — FastAPI + Webhook.
"""

from fastapi import FastAPI, Request
from handlers.router import handle_message
from handlers.callback_router import handle_callback

app = FastAPI()

@app.get("/")
def home():
    """
    HE: נקודת בדיקה פשוטה לוודא שהשרת רץ.
    EN: Simple health-check endpoint to verify the server is running.
    """
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    """
    HE: נקודת ה-Webhook — טלגרם שולח לכאן כל עדכון (הודעה / כפתור).
    EN: Webhook endpoint — Telegram sends every update here (message / callback).
    """
    data = await request.json()
    print("Incoming:", data)  # HE: לוג לדיבוג | EN: Debug log

    # HE: הודעת טקסט / מדיה
    # EN: Text / media message
    if "message" in data:
        await handle_message(data["message"])

    # HE: לחיצה על כפתור Inline
    # EN: Inline button click
    if "callback_query" in data:
        await handle_callback(data["callback_query"])

    # HE: טלגרם דורש תשובה כלשהי כדי לא לנסות שוב.
    # EN: Telegram requires a response to avoid retrying.
    return {"ok": True}
