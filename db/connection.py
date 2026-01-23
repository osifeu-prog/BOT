import sqlite3
import os
from utils.config import DATABASE_URL

def get_conn():
    # פונקציה מרכזית שכל האדמין והראוטר מחפשים
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Starter'
        )
    ''')
    conn.commit()
    conn.close()
