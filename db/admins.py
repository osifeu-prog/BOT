"""
db/admins.py
=============
ניהול טבלת המנהלים (admins).

מטרתו:
- לבדוק האם משתמש הוא מנהל
- להוסיף מנהל חדש
- לדאוג שהטבלה תמיד קיימת לפני INSERT/SELECT
"""

from db.connection import get_conn

def _ensure_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

def is_admin(user_id):
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def add_admin(user_id):
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute(
        "INSERT INTO admins (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (user_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
