"""
main.py
========
זהו קובץ הכניסה הראשי של הבוט.

מה הוא עושה?
-------------
1. מגדיר אפליקציית FastAPI — מסגרת פייתון ליצירת API.
2. מגדיר את ה־Webhook — הכתובת שטלגרם שולח אליה עדכונים.
3. מקבל כל עדכון מטלגרם (הודעה / כפתור).
4. מנתב את העדכון לקבצים המתאימים:
   - handle_message  → הודעות טקסט / מדיה
   - handle_callback → לחיצות על כפתורי Inline
5. מחזיר תשובה לטלגרם כדי לא לקבל שגיאות.

זהו "שער הכניסה" של כל המערכת.
"""
from fastapi import FastAPI, Request
from handlers.router import handle_message
from handlers.callback_router import handle_callback

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Incoming:", data)

    if "message" in data:
        await handle_message(data["message"])

    if "callback_query" in data:
        await handle_callback(data["callback_query"])

    return {"ok": True}
