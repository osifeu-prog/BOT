"""
buyers.py
=========
HE: ניהול טבלת רוכשים — מי קנה את הקורס/המערכת.
EN: Buyers table management — who purchased the course/system.
"""

from db.connection import get_conn
from utils.edu_log import edu_step, edu_success

def _ensure_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            user_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

def is_buyer(user_id: int) -> bool:
    """
    HE: בודק אם המשתמש הוא רוכש.
    EN: Checks if the user is a buyer.
    """
    edu_step(1, f"Checking if user {user_id} is buyer.")
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute("SELECT 1 FROM buyers WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def add_buyer(user_id: int):
    """
    HE: מוסיף רוכש חדש.
    EN: Adds a new buyer.
    """
    edu_step(1, f"Adding buyer {user_id}.")
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
    edu_success(f"Buyer {user_id} added.")
