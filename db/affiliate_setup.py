from db.connection import get_conn

def add_referrer_column():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # הוספת עמודת ה-referrer לטבלת המשתמשים
            cur.execute("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS referred_by BIGINT;")
            conn.commit()
    print("✅ Affiliate System Column Added!")

if __name__ == "__main__":
    add_referrer_column()
