from db.connection import get_conn
from db.events import _ensure_table as ensure_events
from db.buyers import _ensure_table as ensure_buyers
from db.admins import _ensure_table as ensure_admins

def init():
    print("?? Initializing Database Tables...")
    conn = get_conn()
    cur = conn.cursor()
    
    # ????? ??????? ????????
    ensure_events(cur)
    ensure_buyers(cur)
    ensure_admins(cur)
    
    # ????? ???? ????????? ????? (?? ?? ?????)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            result TEXT,
            payout INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("? Database Ready!")

if __name__ == "__main__":
    init()
