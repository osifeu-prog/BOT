from db.connection import get_conn
from datetime import datetime, timedelta

def get_user_stats(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT xp, slh_coins, balance, last_daily FROM users WHERE user_id = %s", (str(user_id),))
    res = cur.fetchone()
    cur.close(); conn.close()
    return res if res else (0, 100, 0, None)

def update_user_economy(user_id, xp_add=0, slh_add=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET xp = xp + %s, slh_coins = slh_coins + %s WHERE user_id = %s", (xp_add, slh_add, str(user_id)))
    conn.commit()
    cur.close(); conn.close()

def claim_daily(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT last_daily FROM users WHERE user_id = %s", (str(user_id),))
    last = cur.fetchone()[0]
    now = datetime.now()
    if last and now - last < timedelta(days=1):
        cur.close(); conn.close(); return False
    cur.execute("UPDATE users SET slh_coins = slh_coins + 50, last_daily = %s WHERE user_id = %s", (now, str(user_id)))
    conn.commit()
    cur.close(); conn.close(); return True

def get_leaderboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, slh_coins FROM users ORDER BY slh_coins DESC LIMIT 5")
    res = cur.fetchall()
    cur.close(); conn.close()
    return res

def transfer_slh(from_id, to_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT slh_coins FROM users WHERE user_id = %s", (str(from_id),))
        if cur.fetchone()[0] < amount: return False
        cur.execute("UPDATE users SET slh_coins = slh_coins - %s WHERE user_id = %s", (amount, str(from_id)))
        cur.execute("UPDATE users SET slh_coins = slh_coins + %s WHERE user_id = %s", (amount, str(to_id)))
        conn.commit(); return True
    except: return False
    finally: cur.close(); conn.close()
