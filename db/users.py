from db.connection import get_conn

def update_user_economy(user_id, slh_add=0, xp_add=0, bal_add=0):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # בדיקה אם המשתמש קיים, אם לא - יצירה
        cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", (user_id,))
        
        # עדכון עם מרכאות כפולות לשם העמודה כדי למנוע טעויות זיהוי
        query = '''
            UPDATE users 
            SET "slh" = GREATEST(0, COALESCE("slh", 0) + %s), 
                "xp" = COALESCE("xp", 0) + %s, 
                "balance" = COALESCE("balance", 0) + %s 
            WHERE user_id = %s
        '''
        cur.execute(query, (slh_add, xp_add, bal_add, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ DB Update Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_user_stats(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT xp, "slh", balance, language FROM users WHERE user_id = %s', (user_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res if res else (0, 0, 0, 'he')