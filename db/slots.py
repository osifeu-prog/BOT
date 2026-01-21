"""
slots.py
========
HE: טבלת היסטוריית משחק SLOTS.
EN: Slots game history table.
"""

from db.connection import get_conn
from utils.edu_log import edu_step

def _ensure_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

def add_slots_result(user_id: int, result: str):
    """
    HE: מוסיף תוצאה חדשה למשחק.
    EN: Adds a new game result.
    """
    edu_step(1, f"Adding slots result for user {user_id}: {result}")
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute(
        "INSERT INTO slots_history (user_id, result) VALUES (%s, %s)",
        (user_id, result)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_leaderboard(limit: int = 10):
    """
    HE: מחזיר טבלת מובילים לפי מספר משחקים.
    EN: Returns leaderboard by number of games played.
    """
    edu_step(1, "Fetching leaderboard.")
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute("""
        SELECT user_id, COUNT(*) as plays
        FROM slots_history
        GROUP BY user_id
        ORDER BY plays DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
