import psycopg2
from utils.config import DATABASE_URL

def get_conn():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise e
