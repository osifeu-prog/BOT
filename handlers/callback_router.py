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
    data = callback["data"]

    if data.startswith("menu_"):
        return await menu_callback(callback)
