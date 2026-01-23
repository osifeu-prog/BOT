import psycopg2
import os
from dotenv import load_dotenv

# טעינה ישירה של המשתנים מהסביבה (Railway)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def init_db():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment variables!")
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # טבלת משתמשים - הלב של האימפריה
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance BIGINT DEFAULT 200,
            xp INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Starter',
            is_vip BOOLEAN DEFAULT FALSE,
            referred_by TEXT,
            last_daily TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # טבלת יומן שוק - הדלק ל-AI
        cur.execute('''CREATE TABLE IF NOT EXISTS journal (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            entry TEXT,
            sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # טבלת רכישות SaaS - המודל העסקי
        cur.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            bot_type TEXT,
            expiry_date TIMESTAMP
        )''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("--- PostgreSQL Tables Created Successfully ---")
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    init_db()
