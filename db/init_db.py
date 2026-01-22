from db.connection import get_conn

def init_tables():
    commands = [
        """CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            referred_by BIGINT,
            joined_at TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS buyers (
            user_id BIGINT PRIMARY KEY,
            purchase_date TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            result TEXT,
            payout INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            event_type TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )"""
    ]
    try:
        conn = get_conn()
        cur = conn.cursor()
        for cmd in commands:
            cur.execute(cmd)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tables initialized successfully")
    except Exception as e:
        print(f"⚠️ DB Init Warning: {e}")
