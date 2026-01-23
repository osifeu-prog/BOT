from db.connection import get_conn

def log_event(user_id, event_type, details=""):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_events (user_id, event_type, details) VALUES (%s, %s, %s)", (user_id, event_type, details))
        conn.commit()
        conn.close()
    except:
        pass
