# handlers/callback_router.py

"""
Router ללחיצות על כפתורי Inline (callback_query).
"""

from callbacks.menu import menu_callback
from callbacks.course import course_callback

async def handle_callback(callback):
    data = callback["data"]

    if data.startswith("menu_"):
        return await menu_callback(callback)

    if data.startswith("course|"):
        return await course_callback(callback)
