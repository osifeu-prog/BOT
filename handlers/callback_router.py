"""
callback_router.py
==================
HE: מנתב לחיצות על כפתורי Inline לפונקציות המתאימות.
EN: Routes inline button clicks to the appropriate handlers.
"""

from callbacks.menu import menu_callback
from callbacks.course import course_callback

async def handle_callback(callback: dict):
    """
    HE: נקודת הכניסה לכל callback_query.
    EN: Entry point for every callback_query.
    """
    data = callback["data"]

    if data.startswith("menu_"):
        return await menu_callback(callback)

    if data.startswith("course|"):
        return await course_callback(callback)
