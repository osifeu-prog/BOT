import sqlite3
from datetime import datetime

DB_PATH = "diamond_bot.db"

def update_user_balance(user_id, amount, currency="slh"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    column = "slh_balance" if currency == "slh" else "balance"
    cursor.execute(f"UPDATE users SET {column} = {column} + ? WHERE telegram_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def transfer_funds(from_id, to_id, amount, currency="slh"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # בדיקת יתרה
        column = "slh_balance" if currency == "slh" else "balance"
        cursor.execute(f"SELECT {column} FROM users WHERE telegram_id = ?", (from_id,))
        balance = cursor.fetchone()[0]
        if balance < amount:
            return False, "יתרה נמוכה מדי"
        
        # ביצוע העברה
        cursor.execute(f"UPDATE users SET {column} = {column} - ? WHERE telegram_id = ?", (amount, from_id))
        cursor.execute(f"UPDATE users SET {column} = {column} + ? WHERE telegram_id = ?", (amount, to_id))
        conn.commit()
        return True, "העברה בוצעה בהצלחה"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, username, slh_balance, balance FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
