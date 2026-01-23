import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def patch_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Checking database structure...")
    # הוספת עמודת rank אם היא לא קיימת
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS rank TEXT DEFAULT 'Starter',
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database patched successfully: 'rank' column added.")

if __name__ == "__main__":
    patch_db()
