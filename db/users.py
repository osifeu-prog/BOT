from db.connection import get_conn

def update_user_economy(user_id, slh_add=0, xp_add=0, bal_add=0):
    conn = get_conn()
    cur = conn.cursor()
    # שימוש ב-GREATEST כדי למנוע יתרה שלילית (הגנה מפני גניבות)
    cur.execute('''
        UPDATE users 
        SET slh = GREATEST(0, slh + %s), 
            xp = xp + %s, 
            balance = balance + %s 
        WHERE user_id = %s
    ''', (slh_add, xp_add, bal_add, user_id))
    conn.commit()
    cur.close()
    conn.close()

def transfer_slh(sender_id, receiver_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # בדיקה שהשולח קיים ויש לו מספיק כסף (Atomic Transaction)
        cur.execute("SELECT slh FROM users WHERE user_id = %s", (sender_id,))
        res = cur.fetchone()
        if res and res[0] >= amount:
            cur.execute("UPDATE users SET slh = slh - %s WHERE user_id = %s", (amount, sender_id))
            cur.execute("UPDATE users SET slh = slh + %s WHERE user_id = %s", (amount, receiver_id))
            conn.commit()
            return True
        return False
    finally:
        cur.close()
        conn.close()

def get_user_stats(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT xp, slh, balance, language FROM users WHERE user_id = %s", (user_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res if res else (0, 0, 0, 'he')

def get_leaderboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, slh FROM users ORDER BY slh DESC LIMIT 5")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res