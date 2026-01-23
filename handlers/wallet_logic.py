import logging
from db.connection import get_conn

def get_user_full_data(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance, xp, rank, wallet_address FROM users WHERE user_id = %s", (str(user_id),))
    row = cur.fetchone()
    conn.close()
    return row if row else (0.0, 0, "Beginner", None)

def register_user(user_id, ref_by=None):
    """רושם משתמש חדש במערכת אם אינו קיים."""
    conn = get_conn()
    cur = conn.cursor()
    # בדיקה אם המשתמש כבר קיים
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (str(user_id),))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 0.0)", (str(user_id),))
        logging.info(f"User {user_id} registered. Referred by: {ref_by}")
        # כאן אפשר להוסיף לוגיקה למתן בונוס למזמין (ref_by) בעתיד
    conn.commit()
    conn.close()

def get_last_transactions(user_id, limit=5):
    """מושך את העסקאות האחרונות של המשתמש."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT amount, type, timestamp FROM transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s", (str(user_id), limit))
    rows = cur.fetchall()
    conn.close()
    # המרה לפורמט קריא: (כמות, סוג/תאריך)
    return [(r[0], r[2].strftime("%d/%m %H:%M")) for r in rows]

def claim_airdrop(user_id, wallet_addr):
    """מבצע את חלוקת האירדרופ ושומר כתובת ארנק."""
    conn = get_conn()
    cur = conn.cursor()
    
    # עדכון כתובת ארנק
    cur.execute("UPDATE users SET wallet_address = %s WHERE user_id = %s", (wallet_addr, str(user_id)))
    
    # בדיקה אם כבר קיבל אירדרופ (לפי טבלת טרנזקציות)
    cur.execute("SELECT id FROM transactions WHERE user_id = %s AND type = 'airdrop'", (str(user_id),))
    if cur.fetchone():
        conn.close()
        return False, "כבר קיבלת את האירדרופ שלך!"

    # משיכת סכום האירדרופ מההגדרות (ברירת מחדל 5.0)
    cur.execute("SELECT value FROM settings WHERE key = 'airdrop_amount'")
    row = cur.fetchone()
    amount = float(row[0]) if row else 5.0

    # ביצוע ההפקדה
    cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, str(user_id)))
    cur.execute("INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, 'airdrop')", (str(user_id), amount))
    
    conn.commit()
    conn.close()
    return True, amount
