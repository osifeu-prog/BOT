import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("DB_MANAGER")

def get_conn():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    # פקודות SQL נפרדות למניעת שגיאות סינטקס
    commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS rank TEXT DEFAULT 'Starter'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS wallet_address TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_daily TIMESTAMP",
        "CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, sender_id TEXT, receiver_id TEXT, amount FLOAT, type TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS gifts (id SERIAL PRIMARY KEY, code TEXT UNIQUE, creator_id TEXT, amount FLOAT, is_redeemed BOOLEAN DEFAULT FALSE, redeemed_by TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ]
    
    logger.info("--- Starting Database Migrations ---")
    for cmd in commands:
        try:
            cursor.execute(cmd)
            conn.commit()
            logger.info(f"SUCCESS: {cmd[:40]}...")
        except Exception as e:
            conn.rollback()
            logger.warning(f"SKIPPED/ERROR: {cmd[:40]} | Reason: {e}")
            
    conn.close()
    logger.info("--- Database Migrations Finished ---")

# הרצה בזמן טעינה
init_db()
