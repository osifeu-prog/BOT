# handlers/callback_router.py

"""
Router ללחיצות על כפתורי Inline.
פתוח לכולם — אין סינון לפי מנהלים.
"""

from callbacks.menu import menu_callback

async def handle_callback(callback):
    data = callback["data"]

    if data.startswith("menu_"):
        return await menu_callback(callback)
