from db.connection import get_conn
import logging

logger = logging.getLogger("SLH_OS")

def record_transaction(user_id, amount, tx_type):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, %s)", 
                    (str(user_id), float(amount), tx_type))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def transfer_funds(sender_id, receiver_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        amount = float(amount)
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (str(sender_id),))
        b = cur.fetchone()
        if not b or b[0] < amount: return False, "Insufficient funds"
        
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, str(sender_id)))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, str(receiver_id)))
        conn.commit()
        record_transaction(sender_id, -amount, 'TRANSFER')
        record_transaction(receiver_id, amount, 'TRANSFER')
        logger.info(f"💸 TX: {sender_id} -> {receiver_id} ({amount} SLH)")
        return True, "Success"
    except Exception as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def get_economy_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT SUM(balance), COUNT(*) FROM users")
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res[0] or 0, res[1] or 0

def get_user_full_data(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance, xp, rank FROM users WHERE user_id = %s", (str(user_id),))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data if data else (0, 0, "Guest")

def register_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (str(user_id),))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 100)", (str(user_id),))
        conn.commit()
        logger.info(f"👤 New User Registered: {user_id}")
    cur.close()
    conn.close()
