from db.connection import get_conn

def add_user(user_id, referrer_id=None):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (user_id, referred_by) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (user_id, referrer_id))
        conn.commit()
        conn.close()
    except:
        pass
