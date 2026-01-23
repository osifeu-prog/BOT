import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    # פקודות השדרוג
    commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS rank TEXT DEFAULT 'Starter'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS wallet_address TEXT",
        "CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, sender_id TEXT, receiver_id TEXT, amount FLOAT, type TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS gifts (id SERIAL PRIMARY KEY, code TEXT UNIQUE, creator_id TEXT, amount FLOAT, is_redeemed BOOLEAN DEFAULT FALSE, redeemed_by TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ]
    
    for cmd in commands:
        try:
            cursor.execute(cmd)
        except Exception as e:
            print(f"Migration Notice: {e}")
            conn.rollback()
            continue
            
    conn.commit()
    conn.close()

# הרצה אוטומטית של המיגרציה בכל פעם שהמודול נטען
init_db()
