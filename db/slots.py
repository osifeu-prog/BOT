"""
db/slots.py
============
אחראי על שמירת תוצאות משחק ה-SLOTS.

שני מקומות:
1. PostgreSQL — היסטוריה מלאה של כל משחק.
2. Redis — ניקוד חי לטבלת מובילים (leaderboard).
"""
from db.connection import get_conn

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
