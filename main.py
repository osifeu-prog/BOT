"""
main.py
========
זה קובץ הכניסה של הבוט.

מה הוא עושה?
- מגדיר אפליקציית FastAPI
- מגדיר את ה-endpoint /webhook שאליו טלגרם שולח עדכונים
- קורא את ה-JSON שמגיע מטלגרם
- מזהה אם מדובר בהודעה רגילה (message) או לחיצה על כפתור (callback_query)
- מעביר את הטיפול לקבצים המתאימים:
  - handle_message להודעות טקסט / מדיה
  - handle_callback ללחיצות על כפתורי Inline
"""

from fastapi import FastAPI, Request
from handlers.router import handle_message
from handlers.callback_router import handle_callback

app = FastAPI()

@app.get("/")
def home():
    """
    נקודת בדיקה פשוטה.

    למה זה טוב?
    - כדי לבדוק שהשרת חי (Health Check)
    - אפשר לפתוח את ה-URL בדפדפן ולראות שהבוט רץ
    """
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    """
    זו הפונקציה שטלגרם קורא לה בכל פעם שיש עדכון חדש.

    מה קורה כאן?
    1. קוראים את גוף הבקשה כ-JSON.
    2. אם יש "message" → מעבירים ל-handle_message.
    3. אם יש "callback_query" → מעבירים ל-handle_callback.
    4. מחזירים {"ok": True} כדי שטלגרם ידע שהכל עבר בהצלחה.
    """
    data = await request.json()
    print("Incoming:", data)  # לוג לצורך דיבוג

    if "message" in data:
        await handle_message(data["message"])

    if "callback_query" in data:
        await handle_callback(data["callback_query"])

    return {"ok": True}
