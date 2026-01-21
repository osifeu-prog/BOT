"""
callbacks/course.py
====================
מטפל בשיעורי הקורס (Markdown בעמודים).

callback_data בפורמט:
course|LESSON_KEY|page_index

לדוגמה:
course|TELEGRAM_UI|0
"""

from utils.telegram import send_message
from utils.content import load_markdown_pages
from db.course_progress import get_course_page, set_course_page

# מיפוי בין lesson_key לבין שם קובץ ה-Markdown
LESSON_FILES = {
    "TELEGRAM_UI": "TELEGRAM_UI.md",
    "HOW_IT_WORKS": "HOW_IT_WORKS.md",
    "INSTALL": "INSTALL.md",
    "ARCH": "ARCHITECTURE.md",
    "CUSTOMIZE": "CUSTOMIZE.md",
    "SLOTS_CODE": "SLOTS_CODE.md",
    "TEMPLATE": "TEMPLATE.md",
    "FULL_CODE": "FULL_CODE_EXPLAINED.md",
}

async def send_lesson_page(user_id: int, lesson_key: str, page_index: int = 0):
    """
    שולח עמוד מסוים מתוך שיעור.

    - טוען את כל העמודים
    - בוחר את העמוד לפי page_index
    - בונה כפתור "המשך" אם יש עוד עמודים
    - שומר התקדמות ב-Redis
    """
    filename = LESSON_FILES.get(lesson_key)
    if not filename:
        return await send_message(user_id, "⚠️ השיעור לא נמצא.")

    pages = load_markdown_pages(filename)
    if not pages:
        return await send_message(user_id, "⚠️ השיעור ריק.")

    # הגנה על אינדקס
    if page_index < 0:
        page_index = 0
    if page_index >= len(pages):
        page_index = len(pages) - 1

    text = pages[page_index]

    # שמירת התקדמות
    set_course_page(user_id, lesson_key, page_index)

    # בניית כפתור "המשך" אם יש עוד עמודים
    buttons = []
    if page_index < len(pages) - 1:
        next_data = f"course|{lesson_key}|{page_index + 1}"
        buttons.append([{"text": "המשך ▶️", "callback_data": next_data}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None

    await send_message(user_id, text, reply_markup=reply_markup)

async def course_callback(callback):
    """
    מטפל ב-callback_data בפורמט:
    course|LESSON_KEY|page_index
    """
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    try:
        _, lesson_key, page_str = data.split("|", 2)
        page_index = int(page_str)
    except ValueError:
        return await send_message(user_id, "⚠️ שגיאה בקריאת השיעור.")

    await send_lesson_page(user_id, lesson_key, page_index)
