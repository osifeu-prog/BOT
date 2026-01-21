"""
db/admins.py
=============
ניהול טבלת המנהלים (admins).

מטרתו:
- לבדוק האם משתמש הוא מנהל
- להוסיף מנהל חדש
"""

from db.connection import get_conn

def is_admin(user_id):
    """
    בודק האם user_id קיים בטבלת admins.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def add_admin(user_id):
    """
    מוסיף משתמש לטבלת admins (אם הוא לא קיים כבר).
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO admins (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (user_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
