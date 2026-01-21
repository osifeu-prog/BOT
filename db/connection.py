import psycopg2
from utils.config import DB_URL

def get_conn():
    return psycopg2.connect(DB_URL)
