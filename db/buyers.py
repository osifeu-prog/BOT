"""
db/buyers.py
=============
ניהול רשימת הרוכשים של הקורס/הפרויקט.

מטרתו:
- לבדוק האם משתמש רכש
- להוסיף רוכש חדש (אחרי אישור תשלום)
"""
from db.connection import get_conn

def _ensure_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            user_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

def is_buyer(user_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute("SELECT 1 FROM buyers WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def add_buyer(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute(
        "INSERT INTO buyers (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (user_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
