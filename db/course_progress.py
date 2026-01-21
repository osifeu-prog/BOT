"""
db/course_progress.py
======================
שומר התקדמות של משתמשים בקורס (איזה עמוד הם כרגע בכל שיעור).

שימוש:
- set_course_page(user_id, lesson_key, page_index)
- get_course_page(user_id, lesson_key) -> int
"""

import redis
from utils.config import REDIS_URL

r = redis.from_url(REDIS_URL) if REDIS_URL else None

def _key(user_id: int, lesson_key: str) -> str:
    return f"course:{user_id}:{lesson_key}"

def set_course_page(user_id: int, lesson_key: str, page_index: int):
    if not r:
        return
    r.set(_key(user_id, lesson_key), page_index)

def get_course_page(user_id: int, lesson_key: str) -> int:
    if not r:
        return 0
    value = r.get(_key(user_id, lesson_key))
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0
