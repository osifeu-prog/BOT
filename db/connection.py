import psycopg2
import os
from utils.config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    commands = [
        "CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, balance REAL DEFAULT 0.0, xp INTEGER DEFAULT 0, rank TEXT DEFAULT 'Beginner', wallet_address TEXT)",
        "CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id TEXT, amount REAL, type TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, block_hash TEXT)",
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)",
        # פקודת בטיחות: מוודאת שהעמודה קיימת גם אם הטבלה נוצרה פעם בלי
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ]

    for cmd in commands:
        try:
            cursor.execute(cmd)
        except:
            conn.rollback()
            continue

    conn.commit()
    conn.close()
