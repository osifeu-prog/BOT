from db.connection import get_conn

def update_user_economy(user_id, xp_add=0, slh_add=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET xp = xp + %s, slh_coins = slh_coins + %s WHERE user_id = %s", 
                (xp_add, slh_add, str(user_id)))
    conn.commit()
    cur.close()
    conn.close()

def get_user_stats(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT xp, slh_coins, balance FROM users WHERE user_id = %s", (str(user_id),))
    res = cur.fetchone()
    cur.close(); conn.close()
    return res if res else (0, 100, 0)
