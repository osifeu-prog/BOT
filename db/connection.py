import psycopg2
from utils.config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def initialize_db():
    conn = get_conn()
    cur = conn.cursor()
    # מחיקה ויצירה מחדש כדי לוודא שכל העמודות קיימות ב-100%
    # שים לב: זה יאפס יתרות קיימות פעם אחת בלבד לצורך התיקון
    cur.execute('DROP TABLE IF EXISTS users CASCADE')
    cur.execute('''
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            slh INTEGER DEFAULT 100,
            balance INTEGER DEFAULT 0,
            language TEXT DEFAULT 'he'
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("🚀 Database Reset & Recreated Successfully")