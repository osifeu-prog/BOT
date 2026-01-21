"""
main.py
========
זה קובץ הכניסה של הבוט.

מה הוא עושה?
- מגדיר אפליקציית FastAPI
- מגדיר את ה-endpoint /webhook שאליו טלגרם שולח עדכונים
- מנתב כל עדכון להנדלרים המתאימים:
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
    מאפשרת לוודא שהשרת חי (למשל דרך דפדפן או curl).
    """
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    """
    זו הפונקציה שטלגרם קורא לה בכל פעם שיש עדכון חדש.

    מה קורה כאן?
    1. קוראים את ה-JSON שנשלח מטלגרם.
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
