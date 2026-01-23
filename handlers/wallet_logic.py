import sqlite3
from utils.config import DATABASE_URL
from db.connection import get_conn

def register_user(user_id, referrer_id=None):
    conn = get_conn()
    cur = conn.cursor()
    
    # בדיקה אם המשתמש כבר קיים
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (str(user_id),))
    if cur.fetchone():
        conn.close()
        return False

    # רישום משתמש חדש עם Airdrop של 10 SLH
    cur.execute("INSERT INTO users (user_id, balance, referrer_id) VALUES (%s, 10.0, %s)", 
                (str(user_id), str(referrer_id) if referrer_id else None))
    
    # בונוס למזמין (5 SLH)
    if referrer_id:
        cur.execute("UPDATE users SET balance = balance + 5.0 WHERE user_id = %s", (str(referrer_id),))
        
    conn.commit()
    conn.close()
    return True

def get_user_full_data(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance, xp, rank, wallet_address FROM users WHERE user_id = %s", (str(user_id),))
    res = cur.fetchone()
    conn.close()
    return res if res else (0, 0, "Beginner", "None")
