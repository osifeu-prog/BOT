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
    
    # أ—آ¤أ—آ§أ—â€¢أ—â€œأ—â€¢أ—ع¾ أ—â€‌أ—آ©أ—â€œأ—آ¨أ—â€¢أ—â€™
    commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS rank TEXT DEFAULT 'Starter'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS wallet_address TEXT, last_daily TIMESTAMP",
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

# أ—â€‌أ—آ¨أ—آ¦أ—â€‌ أ—ع¯أ—â€¢أ—ع©أ—â€¢أ—â€چأ—ع©أ—â„¢أ—ع¾ أ—آ©أ—إ“ أ—â€‌أ—â€چأ—â„¢أ—â€™أ—آ¨أ—آ¦أ—â„¢أ—â€‌ أ—â€کأ—â€؛أ—إ“ أ—آ¤أ—آ¢أ—â€Œ أ—آ©أ—â€‌أ—â€چأ—â€¢أ—â€œأ—â€¢أ—إ“ أ—آ أ—ع©أ—آ¢أ—ع؛
init_db()


