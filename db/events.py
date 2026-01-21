from db.connection import get_conn

def log_event(user_id, event_type, event_key, payload=None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            event_key TEXT NOT NULL,
            payload TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        '''
    )

    cur.execute(
        "INSERT INTO user_events (user_id, event_type, event_key, payload) VALUES (%s, %s, %s, %s)",
        (user_id, event_type, event_key, payload)
    )

    conn.commit()
    cur.close()
    conn.close()
