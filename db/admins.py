import os
from db.connection import get_conn

def _ensure_table(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY
        )
    ''')

def is_admin(user_id):
    # בדיקה מהירה מול משתנה סביבה (למקרה שה-DB עוד לא מעודכן)
    env_admin = os.getenv("ADMIN_ID")
    if env_admin and str(user_id) == str(env_admin):
        return True
        
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        exists = cur.fetchone() is not None
        cur.close()
        conn.close()
        return exists
    except:
        return False
