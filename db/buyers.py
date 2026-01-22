from db.connection import get_conn

def _ensure_table(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS buyers (
            user_id BIGINT PRIMARY KEY,
            purchase_date TIMESTAMP DEFAULT NOW()
        )
    ''')

def is_buyer(user_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM buyers WHERE user_id = %s", (user_id,))
        exists = cur.fetchone() is not None
        cur.close()
        conn.close()
        return exists
    except Exception as e:
        print(f"Error checking buyer: {e}")
        return False

def add_buyer(user_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO buyers (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error adding buyer: {e}")
