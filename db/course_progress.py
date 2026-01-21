"""
course_progress.py
==================
HE: שמירת התקדמות בקורס ב-Redis (איזה עמוד בכל שיעור).
EN: Storing course progress in Redis (which page in each lesson).
"""

import redis
from utils.config import REDIS_URL
from utils.edu_log import edu_step

r = redis.from_url(REDIS_URL) if REDIS_URL else None

def _key(user_id: int, lesson_key: str) -> str:
    return f"course:{user_id}:{lesson_key}"

def set_course_page(user_id: int, lesson_key: str, page_index: int):
    """
    HE: שומר את העמוד הנוכחי של המשתמש בשיעור.
    EN: Stores the user's current page in a lesson.
    """
    if not r:
        return
    edu_step(1, f"Setting course page: user={user_id}, lesson={lesson_key}, page={page_index}")
    r.set(_key(user_id, lesson_key), page_index)

def get_course_page(user_id: int, lesson_key: str) -> int:
    """
    HE: מחזיר את העמוד האחרון שבו המשתמש היה בשיעור.
    EN: Returns the last page the user visited in a lesson.
    """
    if not r:
        return 0
    value = r.get(_key(user_id, lesson_key))
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0
