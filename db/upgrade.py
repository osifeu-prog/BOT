from db.connection import get_conn
from utils.logger import logger

def upgrade_tables():
    conn = get_conn()
    cur = conn.cursor()
    try:
        # יצירת הטבלה מחדש עם כל העמודות הנכונות
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                lang TEXT DEFAULT 'he',
                xp INTEGER DEFAULT 0,
                slh_coins INTEGER DEFAULT 100,
                balance INTEGER DEFAULT 0,
                referral_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ניסיון להוסיף עמודות אם הטבלה כבר הייתה קיימת
        cols = [("xp", "INTEGER DEFAULT 0"), ("slh_coins", "INTEGER DEFAULT 100"), 
                ("balance", "INTEGER DEFAULT 0"), ("referral_count", "INTEGER DEFAULT 0")]
        for col, spec in cols:
            try: cur.execute(f"ALTER TABLE users ADD COLUMN {col} {spec}")
            except: conn.rollback()
        conn.commit()
        logger.info("✅ Database Structure Verified")
    except Exception as e:
        logger.error(f"❌ DB Fix Error: {e}")
    finally:
        cur.close(); conn.close()
