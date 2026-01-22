from db.connection import get_conn

def is_buyer(user_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM buyers WHERE user_id = %s", (user_id,))
        res = cur.fetchone()
        conn.close()
        return res is not None
    except:
        return False
