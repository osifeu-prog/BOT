"""
admins.py
=========
HE: ניהול טבלת אדמינים — מי יכול לנהל את המערכת.
EN: Admins table management — who can manage the system.
"""

from db.connection import get_conn
from utils.edu_log import edu_step, edu_success

def _ensure_table(cur):
    """
    HE: יוצר את טבלת האדמינים אם היא לא קיימת.
    EN: Creates the admins table if it does not exist.
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

def is_admin(user_id: int) -> bool:
    """
    HE: בודק אם המשתמש הוא אדמין.
    EN: Checks if the user is an admin.
    """
    edu_step(1, f"Checking if user {user_id} is admin.")
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def add_admin(user_id: int):
    """
    HE: מוסיף אדמין חדש.
    EN: Adds a new admin.
    """
    edu_step(1, f"Adding admin {user_id}.")
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
    edu_success(f"Admin {user_id} added.")
