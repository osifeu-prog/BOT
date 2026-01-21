"""
handlers/callback_router.py
============================
Router ללחיצות על כפתורי Inline (callback_query).

מטרתו:
- לקבל callback_query
- להעביר ל-menu_callback אם זה כפתור תפריט
"""

from callbacks.menu import menu_callback

async def handle_callback(callback):
    """
    הפונקציה הזו נקראת מתוך main.py
    והיא אחראית לטפל בכל callback_query שמגיע מטלגרם.
    """
    data = callback["data"]

    # כל כפתור שמתחיל ב-menu_ עובר ל-menu_callback
    if data.startswith("menu_"):
        return await menu_callback(callback)

    # ברירת מחדל — אם בעתיד יהיו callbackים אחרים
    # אפשר להוסיף כאן תנאים נוספים.
