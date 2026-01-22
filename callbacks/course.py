"""
course.py
=========
HE: לוגיקת הצגת הקורס בעמודים, כולל מצב דמו.
EN: Course display logic in pages, including demo mode.
"""

import os
from utils.telegram import send_message
from utils.content import load_markdown_pages
from db.course_progress import set_course_page
from db.buyers import is_buyer
from db.admins import is_admin
from utils.i18n import detect_language_from_telegram, LanguageCode, t
from utils.edu_log import edu_step, edu_path

# HE: מיפוי מפתחות שיעור לקבצי Markdown (לפי שפה)
# EN: Mapping lesson keys to Markdown files (by language)
LESSON_FILES = {
    "he": {
        "INSTALL": "course/he/INSTALL.md",
        "HOW_IT_WORKS": "course/he/HOW_IT_WORKS.md",
        "TELEGRAM_UI": "course/he/TELEGRAM_UI.md",
        "ARCH": "course/he/ARCHITECTURE.md",
        "CUSTOMIZE": "course/he/CUSTOMIZE.md",
        "SLOTS_CODE": "course/he/SLOTS_CODE.md",
        "TEMPLATE": "course/he/TEMPLATE.md",
        "FULL_CODE": "course/he/FULL_CODE_EXPLAINED.md",
        "MARKETING_BOT": "course/he/MARKETING_BOT.md",
        "RESELLING_KIT": "course/he/RESELLING_KIT.md",
        "INIT_DB": "course/he/INIT_DB.md",
    },
    "en": {
        "INSTALL": "course/en/INSTALL.md",
        "HOW_IT_WORKS": "course/en/HOW_IT_WORKS.md",
        "TELEGRAM_UI": "course/en/TELEGRAM_UI.md",
        "ARCH": "course/en/ARCHITECTURE.md",
        "CUSTOMIZE": "course/en/CUSTOMIZE.md",
        "SLOTS_CODE": "course/en/SLOTS_CODE.md",
        "TEMPLATE": "course/en/TEMPLATE.md",
        "FULL_CODE": "course/en/FULL_CODE_EXPLAINED.md",
        "MARKETING_BOT": "course/en/MARKETING_BOT.md",
        "RESELLING_KIT": "course/en/RESELLING_KIT.md",
        "INIT_DB": "course/en/INIT_DB.md",
    },
}

async def send_lesson_page(user_id: int, lesson_key: str, page_index: int, lang: LanguageCode):
    """
    HE: שולח עמוד מסוים מתוך שיעור, עם מצב דמו.
    EN: Sends a specific page from a lesson, with demo mode.
    """
    edu_path("USER → COURSE_SYSTEM")
    edu_step(1, f"Sending lesson page: user={user_id}, lesson={lesson_key}, page={page_index}")

    is_premium = is_buyer(user_id) or is_admin(user_id)

    # HE: מצב דמו — רק העמוד הראשון פתוח למי שלא רכש.
    # EN: Demo mode — only the first page is open for non-buyers.
    if not is_premium and page_index > 0:
        demo_text = t(
            lang,
            he=(
                "זהו סוף גרסת הדמו של השיעור הזה.\n\n"
                "כדי לפתוח את כל הקורס (כולל כל העמודים, כל הקבצים וכל ההסברים):\n\n"
                "💰 עלות: הקורס המלא כפי שמוגדר במערכת.\n"
                "💎 תשלום ב-TON (ראה בתפריט רכישה).\n\n"
                "לאחר התשלום, שלח צילום מסך ותקבל גישה מלאה."
            ),
            en=(
                "This is the end of the demo version of this lesson.\n\n"
                "To unlock the full course (all pages, all files, all explanations):\n\n"
                "💰 Full course price as defined in the system.\n"
                "💎 Pay with TON (see purchase menu).\n\n"
                "After payment, send a screenshot and you'll get full access."
            )
        )
        return send_message(user_id, demo_text)

    filename = LESSON_FILES[lang].get(lesson_key)
    if not filename or not os.path.exists(filename):
        return send_message(
            user_id,
            t(lang, "⚠️ השיעור לא נמצא.", "⚠️ Lesson not found.")
        )

    pages = load_markdown_pages(filename)
    if not pages:
        return send_message(
            user_id,
            t(lang, "⚠️ השיעור ריק.", "⚠️ Lesson is empty.")
        )

    if page_index < 0:
        page_index = 0
    if page_index >= len(pages):
        page_index = len(pages) - 1

    text = pages[page_index]
    set_course_page(user_id, lesson_key, page_index)

    buttons = []
    if page_index < len(pages) - 1:
        next_data = f"course|{lesson_key}|{page_index + 1}"
        buttons.append([{"text": t(lang, "המשך ▶️", "Next ▶️"), "callback_data": next_data}])

    reply_markup = {"inline_keyboard": buttons} if buttons else None
    send_message(user_id, text, reply_markup=reply_markup)

async def course_callback(callback: dict):
    """
    HE: מטפל בכל כפתורי course|...
    EN: Handles all course|... buttons.
    """
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    language_code = callback["from"].get("language_code")
    lang = detect_language_from_telegram(language_code)

    edu_path("USER → CALLBACK → COURSE")
    edu_step(1, f"Course callback: {data!r} from user {user_id}")

    try:
        _, lesson_key, page_str = data.split("|", 2)
        page_index = int(page_str)
    except ValueError:
        return send_message(
            user_id,
            t(lang, "⚠️ שגיאה בקריאת השיעור.", "⚠️ Error reading lesson.")
        )

    await send_lesson_page(user_id, lesson_key, page_index, lang)
