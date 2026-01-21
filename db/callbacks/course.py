from db.buyers import is_buyer
from db.admins import is_admin
from utils.telegram import send_message
# ... השאר כמו קודם ...

async def send_lesson_page(user_id: int, lesson_key: str, page_index: int = 0):
    """
    שולח עמוד מסוים מתוך שיעור.

    לפני הכל:
    - בודק האם המשתמש רכש או שהוא אדמין.
    """
    # רק רוכשים או אדמינים
    if not (is_buyer(user_id) or is_admin(user_id)):
        return await send_message(
            user_id,
            "הקורס זמין רק למי שרכש את הפרויקט.\n\n"
            "כדי לרכוש:\n"
            "💰 עלות: 254 ש\"ח\n"
            "💎 תשלום ב-TON:\n"
            "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp\n\n"
            "לאחר התשלום, שלח צילום מסך ותקבל גישה מלאה לקורס."
        )

    # מכאן והלאה – כמו שכתבנו קודם
    filename = LESSON_FILES.get(lesson_key)
    if not filename:
        return await send_message(user_id, "⚠️ השיעור לא נמצא.")

    pages = load_markdown_pages(filename)
    if not pages:
        return await send_message(user_id, "⚠️ השיעור ריק.")

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

    await send_message(user_id, text, reply_markup=reply_markup)
