from db.connection import get_conn
from utils.logger import logger

def upgrade_tables():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS slh_coins INTEGER DEFAULT 100") # מתנת הצטרפות
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_daily TIMESTAMP")
        conn.commit()
        logger.info("✅ Database Upgraded: SLH Coins and Daily Bonus columns added")
    except Exception as e:
        logger.error(f"❌ DB Upgrade Error: {e}")
    finally:
        cur.close()
        conn.close()
