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

# יוצרים אפליקציית FastAPI
app = FastAPI()


@app.get("/")
def home():
    """
    נקודת בדיקה פשוטה (Health Check).

    למה צריך את זה?
    ----------------
    - Railway / Render / Heroku בודקים שהשרת חי.
    - אתה יכול לפתוח את הכתובת בדפדפן ולראות שהבוט רץ.
    """
    return {"status": "Bot is running"}


@app.post("/webhook")
async def webhook(request: Request):
    """
    זהו ה־Webhook של הבוט.

    כל פעם שמשתמש שולח הודעה לבוט — טלגרם שולח לכאן JSON.

    מה קורה כאן?
    -------------
    1. קוראים את גוף הבקשה (JSON).
    2. בודקים אם מדובר בהודעה רגילה (message).
    3. בודקים אם מדובר בלחיצה על כפתור (callback_query).
    4. מעבירים את העדכון ל־handlers המתאימים.
    5. מחזירים {"ok": True} כדי שטלגרם ידע שהכל עבר בהצלחה.

    חשוב:
    ------
    אם הפונקציה הזו לא מחזירה תשובה — טלגרם יחשוב שהבוט מת.
    """
    data = await request.json()
    print("Incoming:", data)  # לוג חשוב לדיבוג

    # הודעת טקסט / מדיה
    if "message" in data:
        await handle_message(data["message"])

    # לחיצה על כפתור Inline
    if "callback_query" in data:
        await handle_callback(data["callback_query"])

    # טלגרם דורש תשובה כלשהי
    return {"ok": True}
