# -*- coding: utf-8 -*-
from db.connection import get_conn
import logging
import random
from datetime import datetime, timedelta

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

def claim_daily(user_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # בדיקה מתי נלקח לאחרונה
        cursor.execute("SELECT last_daily FROM users WHERE user_id = %s", (str(user_id),))
        last_claimed = cursor.fetchone()[0]
        
        if last_claimed and datetime.now() - last_claimed < timedelta(days=1):
            time_left = timedelta(days=1) - (datetime.now() - last_claimed)
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            conn.close()
            return False, f"{hours} שעות ו-{minutes} דקות"

        # הגרלת סכום ועדכון
        bonus = random.randint(10, 50)
        cursor.execute("UPDATE users SET balance = balance + %s, xp = xp + 5, last_daily = %s WHERE user_id = %s", (bonus, datetime.now(), str(user_id)))
        cursor.execute("INSERT INTO transactions (receiver_id, amount, type) VALUES (%s, %s, 'daily_bonus')", (str(user_id), bonus))
        
        conn.commit()
        conn.close()
        return True, bonus
    except Exception as e:
        logger.error(f"Error claiming daily for {user_id}: {e}")
        return None, str(e)
