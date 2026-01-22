from db.connection import get_conn

def _ensure_table(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            event_type TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')

def log_event(user_id, event_type, details=""):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user_events (user_id, event_type, details) VALUES (%s, %s, %s)",
            (user_id, event_type, details)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error logging event: {e}")
