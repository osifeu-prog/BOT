import psycopg2
from utils.config import DATABASE_URL

TABLES = {
    "user_events": """
        CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """,

    "admins": """
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY
        );
    """,

    "buyers": """
        CREATE TABLE IF NOT EXISTS buyers (
            user_id BIGINT PRIMARY KEY,
            purchased_at TIMESTAMP DEFAULT NOW()
        );
    """,

    "slots_history": """
        CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """
}


def init_db():
    print("🔧 Initializing database...")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for name, ddl in TABLES.items():
        print(f"📌 Ensuring table exists: {name}")
        cur.execute(ddl)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Database initialization complete.")


if __name__ == "__main__":
    init_db()
