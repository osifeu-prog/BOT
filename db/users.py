from db.connection import get_conn

def add_xp(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET xp = xp + %s WHERE user_id = %s", (amount, str(user_id)))
    conn.commit()
    cur.close()
    conn.close()

def get_user_data(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT xp, balance, referral_count FROM users WHERE user_id = %s", (str(user_id),))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data if data else (0, 0, 0)
