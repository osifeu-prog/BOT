import logging, os
from db.connection import get_conn

# משיכת הגדרות מ-Railway Variables
REFERRAL_REWARD = float(os.environ.get('REFERRAL_REWARD', 2.0))

def register_user(user_id, ref_by=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (str(user_id),))
    if not cur.fetchone():
        # רישום משתמש חדש
        cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 0.0)", (str(user_id),))
        logging.info(f"New User: {user_id}")
        
        # אם יש מזמין - תן לו בונוס!
        if ref_by and str(ref_by) != str(user_id):
            cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (REFERRAL_REWARD, str(ref_by)))
            cur.execute("INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, 'referral_bonus')", (str(ref_by), REFERRAL_REWARD))
            logging.info(f"Referral Bonus: {REFERRAL_REWARD} SLH given to {ref_by}")
            
    conn.commit()
    conn.close()

def get_user_full_data(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance, xp, rank, wallet_address FROM users WHERE user_id = %s", (str(user_id),))
    row = cur.fetchone()
    conn.close()
    return row if row else (0.0, 0, "Beginner", None)

def get_last_transactions(user_id, limit=5):
    conn = get_conn()
    cur = conn.cursor()
    # כאן השתמשנו ב-timestamp שסידרנו!
    cur.execute("SELECT amount, type, timestamp FROM transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s", (str(user_id), limit))
    rows = cur.fetchall()
    conn.close()
    return [(r[0], r[2].strftime("%d/%m %H:%M") if r[2] else "N/A") for r in rows]

def manual_transfer(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, str(user_id)))
        cur.execute("INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, 'admin_transfer')", (str(user_id), amount))
        conn.commit()
        return True, f"העברה של {amount} SLH בוצעה!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
