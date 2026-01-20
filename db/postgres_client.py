import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_table():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                message TEXT
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        return "Table ready"
    except Exception as e:
        return f"Postgres error: {e}"

def insert_test_message(msg):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO test_table (message) VALUES (%s)", (msg,))
        conn.commit()
        cur.close()
        conn.close()
        return "Inserted!"
    except Exception as e:
        return f"Insert error: {e}"

def get_messages():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM test_table")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        return f"Select error: {e}"
