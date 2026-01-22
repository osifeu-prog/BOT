import sqlite3
DB_PATH = "database.db"

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, balance, referred_by FROM users WHERE user_id = ?", (str(user_id),))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, 0)", (str(user_id),))
        conn.commit()
        user = (str(user_id), 0, None)
    conn.close()
    return user

def update_user_balance(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, str(user_id)))
    conn.commit()
    conn.close()

def get_total_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(balance) FROM users")
    res = cursor.fetchone()
    conn.close()
    return res
