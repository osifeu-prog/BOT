"""
db/events.py
=============
אחראי על רישום כל פעולה של המשתמש בטבלת user_events.

למה זה חשוב?
- מעקב אחרי שימוש בבוט
- סטטיסטיקות
- ניתוח התנהגות משתמשים
- בסיס ל-Dashboard עתידי
"""from db.connection import get_conn

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

def log_event(user_id: int, event_type: str, data: str = None):
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
