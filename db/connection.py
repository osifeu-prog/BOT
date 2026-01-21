"""
connection.py
=============
HE: חיבור למסד הנתונים (Postgres) דרך DATABASE_URL.
EN: Database connection (Postgres) via DATABASE_URL.
"""

import psycopg2
from utils.config import DATABASE_URL
from utils.edu_log import edu_step, edu_error

def get_conn():
    """
    HE: יוצר חיבור חדש למסד הנתונים.
    EN: Creates a new database connection.
    """
    edu_step(1, "Opening database connection.")
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        edu_error(f"Failed to connect to DB: {e}")
        raise
