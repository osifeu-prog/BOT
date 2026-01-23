import os
import psycopg2
# הסבר: psycopg2-binary מותקן כ-psycopg2, אבל אנחנו מוודאים שהייבוא תקין
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL missing from environment variables")
    
    # תיקון פורמט הכתובת עבור SQLAlchemy/psycopg2
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
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
        print("✅ DB initialized successfully")
    except Exception as e:
        print(f"❌ DB initialization error: {e}")
