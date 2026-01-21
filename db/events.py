"""
events.py
=========
HE: לוג אירועים — מעקב אחרי מה שהמשתמשים עושים.
EN: Events log — tracking what users do.
"""

from db.connection import get_conn
from utils.edu_log import edu_step

def _ensure_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

def log_event(user_id: int, event_type: str, data: str | None = None):
    """
    HE: רושם אירוע חדש בטבלה.
    EN: Logs a new event in the table.
    """
    edu_step(1, f"Logging event: user={user_id}, type={event_type}")
    conn = get_conn()
    cur = conn.cursor()
    _ensure_table(cur)
    cur.execute(
        "INSERT INTO user_events (user_id, event_type, data) VALUES (%s, %s, %s)",
        (user_id, event_type, data)
    )
    conn.commit()
    cur.close()
    conn.close()
