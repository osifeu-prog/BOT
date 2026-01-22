from db.connection import get_conn
from utils.logger import logger

def upgrade_tables():
    conn = get_conn()
    cur = conn.cursor()
    try:
        # יצירת עמודות אחת אחת כדי למנוע קריסה אם חלקן קיימות
        columns = [
            ("xp", "INTEGER DEFAULT 0"),
            ("slh_coins", "INTEGER DEFAULT 100"),
            ("balance", "INTEGER DEFAULT 0"),
            ("referral_count", "INTEGER DEFAULT 0"),
            ("last_daily", "TIMESTAMP")
        ]
        for col_name, col_type in columns:
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added column: {col_name}")
            except:
                conn.rollback() # העמודה כנראה כבר קיימת
        
        conn.commit()
    except Exception as e:
        logger.error(f"❌ DB Upgrade Critical Error: {e}")
    finally:
        cur.close()
        conn.close()
