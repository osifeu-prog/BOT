# callbacks/course.py

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
from db.course_progress import set_course_page
from db.buyers import is_buyer
from db.admins import is_admin

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
    is_premium = is_buyer(user_id) or is_admin(user_id)

    if not is_premium and page_index > 0:
        return send_message(
            user_id,
            "זהו סוף גרסת הדמו של השיעור הזה.\n\n"
            "כדי לפתוח את כל הקורס (כולל כל העמודים, כל הקבצים וכל ההסברים):\n\n"
            "💰 עלות: 254 ש\"ח\n"
            "💎 תשלום ב-TON:\n"
            "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp\n\n"
            "לאחר התשלום, שלח צילום מסך ותקבל גישה מלאה לקורס ולכל הקבצים."
        )

    filename = LESSON_FILES.get(lesson_key)
    if not filename:
        return send_message(user_id, "⚠️ השיעור לא נמצא.")

    pages = load_markdown_pages(filename)
    if not pages:
        return send_message(user_id, "⚠️ השיעור ריק.")

    if page_index < 0:
        page_index = 0
    if page_index >= len(pages):
        page_index = len(pages) - 1

    text = pages[page_index]
    set_course_page(user_id, lesson_key, page_index)

    buttons = []
    if page_index < len(pages) - 1:
        next_data = f"course|{lesson_key}|{page_index + 1}"
        buttons.append([{"text": "המשך ▶️", "callback_data": next_data}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None
    send_message(user_id, text, reply_markup=reply_markup)

async def course_callback(callback):
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    try:
        _, lesson_key, page_str = data.split("|", 2)
        page_index = int(page_str)
    except ValueError:
        return send_message(user_id, "⚠️ שגיאה בקריאת השיעור.")
    await send_lesson_page(user_id, lesson_key, page_index)
