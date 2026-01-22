import psycopg2
from utils.config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def initialize_db():
    conn = get_conn()
    cur = conn.cursor()
    # 1. יצירת הטבלה הבסיסית
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            language TEXT DEFAULT 'he'
        )
    ''')
    
    # 2. הוספת עמודות חסרות במידה ואינן קיימות
    columns_to_add = [
        ("slh", "INTEGER DEFAULT 100"),
        ("balance", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added column {col_name}")
        except psycopg2.errors.DuplicateColumn:
            conn.rollback()
            print(f"ℹ️ Column {col_name} already exists")
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Error adding {col_name}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print("🚀 Database Structure Synced & Ready")