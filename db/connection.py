import psycopg2
import os
from utils.config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def initialize_db():
    conn = get_conn()
    cur = conn.cursor()
    # יצירת טבלאות אם לא קיימות
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            slh INTEGER DEFAULT 100,
            balance INTEGER DEFAULT 0,
            language TEXT DEFAULT 'he'
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables initialized successfully")
    print("🚀 System Online & Upgraded")