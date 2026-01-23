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
    
    # أ—آ¤أ—آ§أ—â€¢أ—â€œأ—â€¢أ—ع¾ SQL أ—آ أ—آ¤أ—آ¨أ—â€œأ—â€¢أ—ع¾ أ—إ“أ—â€چأ—آ أ—â„¢أ—آ¢أ—ع¾ أ—آ©أ—â€™أ—â„¢أ—ع¯أ—â€¢أ—ع¾ أ—طŒأ—â„¢أ—آ أ—ع©أ—آ§أ—طŒ
    commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS rank TEXT DEFAULT 'Starter'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS wallet_address TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_daily TIMESTAMP",
                "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS sender_id TEXT",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS receiver_id TEXT",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS amount FLOAT",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS type TEXT",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS prev_hash TEXT",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS block_hash TEXT",
        "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS block_hash TEXT",
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

# أ—â€‌أ—آ¨أ—آ¦أ—â€‌ أ—â€کأ—â€“أ—â€چأ—ع؛ أ—ع©أ—آ¢أ—â„¢أ—آ أ—â€‌
init_db()


