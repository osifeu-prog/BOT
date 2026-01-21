"""
course.py
=========
HE: לוגיקת הצגת הקורס בעמודים, כולל מצב דמו, רוכשים, אדמינים ושיעורים עסקיים.
EN: Course display logic in pages, including demo mode, buyers, admins and business lessons.
"""

import os
from typing import Dict

from utils.telegram import send_message
from utils.content import load_markdown_pages
from db.course_progress import set_course_page
from db.buyers import is_buyer
from db.admins import is_admin
from utils.i18n import detect_language_from_telegram, LanguageCode, t
from utils.edu_log import edu_step, edu_path, edu_warning

# HE: מיפוי מפתחות שיעור לקבצי Markdown (לפי שפה)
# EN: Mapping lesson keys to Markdown files (by language)
LESSON_FILES: Dict[str, Dict[str, str]] = {
    "he": {
        "INSTALL": "course/he/INSTALL.md",
        "HOW_IT_WORKS": "course/he/HOW_IT_WORKS.md",
        "TELEGRAM_UI": "course/he/TELEGRAM_UI.md",
        "ARCH": "course/he/ARCHITECTURE.md",
        "CUSTOMIZE": "course/he/CUSTOMIZE.md",
        "SLOTS_CODE": "course/he/SLOTS_CODE.md",
        "TEMPLATE": "course/he/TEMPLATE.md",
        "FULL_CODE": "course/he/FULL_CODE_EXPLAINED.md",
        "MARKETING_BOT": "course/he/MARKETING_BOT.md",       # שיעור שיווק הבוט ללקוחות
        "RESELLING_KIT": "course/he/RESELLING_KIT.md",       # שיעור איך למכור את הערכה הלאה
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
        "MARKETING_BOT": "course/en/MARKETING_BOT.md",       # Lesson: marketing the bot to clients
        "RESELLING_KIT": "course/en/RESELLING_KIT.md",       # Lesson: how to resell the kit
    },
}


async def send_lesson_page(
    user_id: int,
    lesson_key: str,
    page_index: int,
    lang: LanguageCode,
) -> None:
    """
    HE:
    ----
    שולח עמוד מסוים מתוך שיעור, כולל:
    - בדיקת האם המשתמש רוכש / אדמין
    - מצב דמו (רק עמוד ראשון פתוח למי שלא רכש)
    - טעינת קובץ ה-Markdown המתאים לשפה
    - חלוקה לעמודים לפי --- PAGE ---
    - שמירת התקדמות ב-Redis

    EN:
    ----
    Sends a specific page from a lesson, including:
    - Checking if the user is a buyer / admin
    - Demo mode (only first page open for non-buyers)
    - Loading the appropriate Markdown file for the language
    - Splitting into pages by --- PAGE ---
    - Storing progress in Redis
    """
    edu_path("USER → COURSE_SYSTEM")
    edu_step(1, f"Sending lesson page: user={user_id}, lesson={lesson_key}, page={page_index}")

    # HE: בדיקה אם המשתמש רוכש או אדמין (גישה מלאה)
    # EN: Check if user is buyer or admin (full access)
    is_premium = is_buyer(user_id) or is_admin(user_id)

    # HE: מצב דמו — רק העמוד הראשון פתוח למי שלא רכש.
    # EN: Demo mode — only the first page is open for non-buyers.
    if not is_premium and page_index > 0:
        edu_warning("User is not premium – demo mode active.")
        demo_text = t(
            lang,
            he=(
                "זהו סוף גרסת הדמו של השיעור הזה.\n\n"
                "כדי לפתוח את כל הקורס (כולל כל העמודים, כל הקבצים וכל ההסברים):\n\n"
                "💰 רכוש את ערכת הסטארטאפ המלאה דרך תפריט הרכישה בבוט.\n"
                "💎 תשלום ב-TON, ולאחר מכן שליחת צילום מסך לאדמין.\n\n"
                "לאחר אישור — תקבל גישה מלאה לכל השיעורים, כולל:\n"
                "- שיווק הבוט ללקוחות\n"
                "- איך למכור את הערכה הלאה\n"
                "- וכל קבצי הקוד המוסברים."
            ),
            en=(
                "This is the end of the demo version of this lesson.\n\n"
                "To unlock the full course (all pages, all files, all explanations):\n\n"
                "💰 Purchase the full startup kit via the bot's purchase menu.\n"
                "💎 Pay with TON, then send a screenshot to the admin.\n\n"
                "Once approved — you'll get full access to all lessons, including:\n"
                "- Marketing the bot to clients\n"
                "- How to resell the kit\n"
                "- And all fully explained code files."
            ),
        )
        return send_message(user_id, demo_text)

    # HE: בחירת קובץ השיעור לפי שפה ומפתח שיעור.
    # EN: Choose the lesson file by language and lesson key.
    filename = LESSON_FILES.get(lang, {}).get(lesson_key)
    if not filename:
        edu_warning(f"Lesson key not found in mapping: lang={lang}, lesson_key={lesson_key}")
        return send_message(
            user_id,
            t(lang, "⚠️ השיעור לא נמצא במפה.", "⚠️ Lesson not found in mapping."),
        )

    if not os.path.exists(filename):
        edu_warning(f"Lesson file does not exist on disk: {filename}")
        return send_message(
            user_id,
            t(lang, "⚠️ קובץ השיעור לא נמצא.", "⚠️ Lesson file not found."),
        )

    # HE: טעינת כל העמודים מהקובץ.
    # EN: Load all pages from the file.
    pages = load_markdown_pages(filename)
    if not pages:
        edu_warning(f"Lesson file is empty or has no pages: {filename}")
        return send_message(
            user_id,
            t(lang, "⚠️ השיעור ריק.", "⚠️ Lesson is empty."),
        )

    # HE: תיקון אינדקסים חריגים (קטן מ-0 או גדול מדי).
    # EN: Fix out-of-range indexes (less than 0 or too large).
    if page_index < 0:
        page_index = 0
    if page_index >= len(pages):
        page_index = len(pages) - 1

    # HE: בחירת הטקסט של העמוד הנוכחי.
    # EN: Choose the text of the current page.
    text = pages[page_index]

    # HE: שמירת התקדמות המשתמש בשיעור (Redis).
    # EN: Store user's progress in the lesson (Redis).
    set_course_page(user_id, lesson_key, page_index)

    # HE: בניית כפתור "המשך" אם יש עוד עמודים.
    # EN: Build "Next" button if there are more pages.
    buttons = []
    if page_index < len(pages) - 1:
        next_data = f"course|{lesson_key}|{page_index + 1}"
        buttons.append(
            [
                {
                    "text": t(lang, "המשך ▶️", "Next ▶️"),
                    "callback_data": next_data,
                }
            ]
        )

    reply_markup = {"inline_keyboard": buttons} if buttons else None

    # HE: שליחת העמוד למשתמש.
    # EN: Send the page to the user.
    send_message(user_id, text, reply_markup=reply_markup)


async def course_callback(callback: dict) -> None:
    """
    HE:
    ----
    מטפל בכל כפתורי course|...
    פורמט ה-data:
        course|<LESSON_KEY>|<PAGE_INDEX>

    דוגמאות:
        course|INSTALL|0
        course|HOW_IT_WORKS|1
        course|MARKETING_BOT|0

    EN:
    ----
    Handles all course|... buttons.
    Data format:
        course|<LESSON_KEY>|<PAGE_INDEX>

    Examples:
        course|INSTALL|0
        course|HOW_IT_WORKS|1
        course|MARKETING_BOT|0
    """
    user_id = callback["message"]["chat"]["id"]
    data = callback["data"]
    language_code = callback["from"].get("language_code")
    lang = detect_language_from_telegram(language_code)

    edu_path("USER → CALLBACK → COURSE")
    edu_step(1, f"Course callback: {data!r} from user {user_id}")

    # HE: ניסיון לפענח את ה-data לפורמט: course|<lesson_key>|<page_index>
    # EN: Try to parse data into: course|<lesson_key>|<page_index>
    try:
        prefix, lesson_key, page_str = data.split("|", 2)
        if prefix != "course":
            raise ValueError("Invalid prefix")
        page_index = int(page_str)
    except Exception as e:
        edu_warning(f"Failed to parse course callback data: {data!r}, error: {e}")
        return send_message(
            user_id,
            t(lang, "⚠️ שגיאה בקריאת השיעור.", "⚠️ Error reading lesson."),
        )

    # HE: שליחת העמוד המתאים.
    # EN: Send the appropriate page.
    await send_lesson_page(user_id, lesson_key, page_index, lang)
