from db.connection import get_conn

def update_user_economy(user_id, slh_add=0, xp_add=0, bal_add=0):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", (user_id,))
        query = '''
            UPDATE users 
            SET "slh" = GREATEST(0, COALESCE("slh", 0) + %s), 
                "xp" = COALESCE("xp", 0) + %s, 
                "balance" = COALESCE("balance", 0) + %s 
            WHERE user_id = %s
        '''
        cur.execute(query, (slh_add, xp_add, bal_add, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ DB Update Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_user_stats(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT xp, "slh", balance, language FROM users WHERE user_id = %s', (user_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res if res else (0, 0, 0, 'he')

def get_leaderboard():
    conn = get_conn()
    cur = conn.cursor()
    # שליפת הטופ 5 לפי SLH
    cur.execute('SELECT user_id, "slh" FROM users ORDER BY "slh" DESC LIMIT 5')
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def transfer_slh(sender_id, receiver_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('SELECT "slh" FROM users WHERE user_id = %s', (sender_id,))
        res = cur.fetchone()
        if res and res[0] >= amount:
            cur.execute('UPDATE users SET "slh" = "slh" - %s WHERE user_id = %s', (amount, sender_id))
            cur.execute('UPDATE users SET "slh" = "slh" + %s WHERE user_id = %s', (amount, receiver_id))
            conn.commit()
            return True
        return False
    finally:
        cur.close()
        conn.close()