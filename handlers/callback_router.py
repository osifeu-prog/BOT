"""
callback_router.py
==================
HE: מנתב לחיצות על כפתורי Inline לפונקציות המתאימות.
EN: Routes inline button clicks to the appropriate handlers.
"""

from callbacks.menu import menu_callback
from callbacks.course import course_callback
from utils.edu_log import edu_step, edu_path

async def handle_callback(callback: dict):
    """
    HE: נקודת הכניסה לכל callback_query.
    EN: Entry point for every callback_query.
    """
    data = callback["data"]
    edu_path("USER → CALLBACK_ROUTER")
    edu_step(1, f"Received callback data: {data!r}")

    if data.startswith("menu_"):
        edu_path("USER → CALLBACK_ROUTER → MENU_CALLBACK")
        return await menu_callback(callback)

    if data.startswith("course|"):
        edu_path("USER → CALLBACK_ROUTER → COURSE_CALLBACK")
        return await course_callback(callback)
