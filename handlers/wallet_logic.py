# -*- coding: utf-8 -*-
from db.connection import get_conn
import logging

logger = logging.getLogger("WALLET_LOGIC")

def get_user_full_data(user_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT balance, xp, rank, wallet_address FROM users WHERE user_id = %s", (str(user_id),))
        res = cursor.fetchone()
        conn.close()
        return res if res else (0, 0, 'Starter', 'None')
    except Exception as e:
        logger.error(f"DB Error for user {user_id}: {e}")
        return (0, 0, 'Error', 'None')

# כאן נוסיף פונקציות שחזור נוספות שרצית
