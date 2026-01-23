import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    DATABASE_URL = os.getenv("DATABASE_URL")
    # בדיקה אם אנחנו ב-Railway (שם הכתובת מתחילה ב-postgres://)
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance FLOAT DEFAULT 0,
            xp INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Beginner',
            wallet_address TEXT,
            referrer_id TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
