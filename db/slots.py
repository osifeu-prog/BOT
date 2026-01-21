"""
db/slots.py
============
אחראי על שמירת תוצאות משחק ה-SLOTS.

שני מקומות:
1. PostgreSQL — היסטוריה מלאה של כל משחק.
2. Redis — ניקוד חי לטבלת מובילים (leaderboard).
"""

import json
import redis
from db.connection import get_conn
from utils.config import REDIS_URL

# חיבור ל-Redis (אם הוגדר REDIS_URL)
r = redis.from_url(REDIS_URL) if REDIS_URL else None

def add_slots_result(user_id, slots, score):
    """
    שומר תוצאה של משחק SLOTS.

    slots — רשימת סמלים (למשל ["🍒", "🍋", "⭐"])
    score — הניקוד שהמשתמש קיבל בסיבוב הזה
    """
    # שמירה ב-PostgreSQL
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            slots TEXT NOT NULL,
            score_change INT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute(
        "INSERT INTO slots_history (user_id, slots, score_change) VALUES (%s, %s, %s)",
        (user_id, json.dumps(slots), score)
    )
    conn.commit()
    cur.close()
    conn.close()

    # ניקוד חי ב-Redis — רק אם יש ניקוד חיובי
    if r and score > 0:
        r.zincrby("slots_leaderboard", score, str(user_id))

def get_leaderboard(limit: int = 10):
    """
    מחזיר את טבלת המובילים מה-Redis.

    אם Redis לא מוגדר — מחזיר רשימה ריקה.
    """
    if not r:
        return []

    leaders = r.zrevrange("slots_leaderboard", 0, limit - 1, withscores=True)
    return [(uid.decode(), score) for uid, score in leaders]
