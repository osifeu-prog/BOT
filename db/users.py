from db.connection import get_conn

def transfer_slh(from_id, to_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # בדיקה שיש מספיק כסף
        cur.execute("SELECT slh_coins FROM users WHERE user_id = %s", (str(from_id),))
        balance = cur.fetchone()[0]
        if balance < amount: return False
        
        # ביצוע ההעברה
        cur.execute("UPDATE users SET slh_coins = slh_coins - %s WHERE user_id = %s", (amount, str(from_id)))
        cur.execute("UPDATE users SET slh_coins = slh_coins + %s WHERE user_id = %s", (amount, str(to_id)))
        conn.commit()
        return True
    except:
        return False
    finally:
        cur.close(); conn.close()

def get_user_stats(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT xp, slh_coins, balance FROM users WHERE user_id = %s", (str(user_id),))
    res = cur.fetchone()
    cur.close(); conn.close()
    return res if res else (0, 100, 0)

def update_user_economy(user_id, xp_add=0, slh_add=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET xp = xp + %s, slh_coins = slh_coins + %s WHERE user_id = %s", 
                (xp_add, slh_add, str(user_id)))
    conn.commit()
    cur.close(); conn.close()
def get_leaderboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, slh_coins FROM users ORDER BY slh_coins DESC LIMIT 5")
    top_users = cur.fetchall()
    cur.close(); conn.close()
    return top_users
