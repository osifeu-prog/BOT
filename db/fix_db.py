from db.connection import get_conn

def fix():
    conn = get_conn()
    cur = conn.cursor()
    try:
        # הוספת העמודה timestamp אם היא חסרה
        cur.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        print("✅ Database schema updated successfully!")
    except Exception as e:
        print(f"❌ Error updating database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix()
