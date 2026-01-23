from db.connection import get_conn
import logging

logger = logging.getLogger(__name__)

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

def mint_to_user(target_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (float(amount), str(target_id)))
        if cur.rowcount == 0:
            return False
        conn.commit()
        record_transaction(target_id, amount, 'MINT')
        return True
    except Exception as e:
        logger.error(f"Mint error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_economy_stats():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT SUM(balance) FROM users")
        total_supply = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0] or 0
        return total_supply, total_users
    finally:
        cur.close()
        conn.close()

def register_user(user_id, referrer_id=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (str(user_id),))
        if cur.fetchone(): return False
        
        cur.execute("INSERT INTO users (user_id, balance, xp, rank, referrer_id) VALUES (%s, %s, %s, %s, %s)", 
                    (str(user_id), 100.0, 10, "Starter", str(referrer_id) if referrer_id else None))
        conn.commit()
        record_transaction(user_id, 100.0, 'AIRDROP')
        
        if referrer_id and str(referrer_id) != str(user_id):
            cur.execute("UPDATE users SET balance = balance + 50 WHERE user_id = %s", (str(referrer_id),))
            conn.commit()
            record_transaction(referrer_id, 50.0, 'REFERRAL')
        return True
    except:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_user_full_data(user_id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT balance, xp, rank, wallet_address FROM users WHERE user_id = %s", (str(user_id),))
        data = cur.fetchone()
        return data if data else (0, 0, "Guest", None)
    finally:
        cur.close()
        conn.close()
