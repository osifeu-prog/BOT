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
        
        # ط£â€”أ¢â‚¬ع©ط£â€”أ¢â‚¬إ“ط£â€”أ¢â€‍آ¢ط£â€”ط¢آ§ط£â€”أ¢â‚¬â€Œ ط£â€”أ¢â‚¬ع†ط£â€”ط¹آ¾ط£â€”أ¢â€‍آ¢ ط£â€”ط¢آ ط£â€”ط¥â€œط£â€”ط¢آ§ط£â€”أ¢â‚¬â€‌ ط£â€”ط¥â€œط£â€”ط¹آ¯ط£â€”أ¢â‚¬â€‌ط£â€”ط¢آ¨ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ ط£â€”أ¢â‚¬â€Œ
        cursor.execute("SELECT last_daily FROM users WHERE user_id = %s", (str(user_id),))
        last_claimed = cursor.fetchone()[0]
        
        if last_claimed and datetime.now() - last_claimed < timedelta(days=1):
            time_left = timedelta(days=1) - (datetime.now() - last_claimed)
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            conn.close()
            return False, f"{hours} ط£â€”ط¢آ©ط£â€”ط¢آ¢ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾ ط£â€”أ¢â‚¬آ¢-{minutes} ط£â€”أ¢â‚¬إ“ط£â€”ط¢آ§ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾"

        # ط£â€”أ¢â‚¬â€Œط£â€”أ¢â‚¬â„¢ط£â€”ط¢آ¨ط£â€”ط¥â€œط£â€”ط¹آ¾ ط£â€”ط·إ’ط£â€”أ¢â‚¬ط›ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬إ’ ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¢ط£â€”أ¢â‚¬إ“ط£â€”أ¢â‚¬ط›ط£â€”أ¢â‚¬آ¢ط£â€”ط¹ط›
        bonus = random.randint(10, 50)
        cursor.execute("UPDATE users SET balance = balance + %s, xp = xp + 5, last_daily = %s WHERE user_id = %s", (bonus, datetime.now(), str(user_id)))
        cursor.execute("INSERT INTO transactions (receiver_id, amount, type) VALUES (%s, %s, 'daily_bonus')", (str(user_id), bonus))
        
        conn.commit()
        conn.close()
        logger.info(f'User {user_id} claimed bonus: {bonus}'); return True, bonus
    except Exception as e:
        logger.error(f"Error claiming daily for {user_id}: {e}")
        return None, str(e)


import hashlib
import json

def generate_hash(data_dict):
    """???? SHA-256 ?????? ?????"""
    encoded = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()

def get_last_hash():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT block_hash FROM transactions ORDER BY id DESC LIMIT 1")
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else "00000000000000000000000000000000"

def secure_transaction(sender_id, receiver_id, amount, tx_type):
    conn = get_conn()
    cursor = conn.cursor()
    
    prev_hash = get_last_hash()
    tx_data = {
        "sender": sender_id,
        "receiver": receiver_id,
        "amount": amount,
        "type": tx_type,
        "prev_hash": prev_hash
    }
    block_hash = generate_hash(tx_data)
    
    cursor.execute(
        "INSERT INTO transactions (sender_id, receiver_id, amount, type, prev_hash, block_hash) VALUES (%s, %s, %s, %s, %s, %s)",
        (str(sender_id), str(receiver_id), amount, tx_type, prev_hash, block_hash)
    )
    conn.commit()
    conn.close()
    return block_hash


def claim_airdrop(user_id, wallet_addr):
    """????? 100 SLH ?????? ????? ???? TON ???? ???????"""
    conn = get_conn()
    cursor = conn.cursor()
    
    # ????? ?? ?????? ??? ???? ??????? ?? ??? ???? ????
    cursor.execute("SELECT wallet_address FROM users WHERE user_id = %s", (str(user_id),))
    current_wallet = cursor.fetchone()
    
    if current_wallet and current_wallet[0] is not None:
        conn.close()
        return False, "??? ????? ???? ????!"

    # ????? ????? ???? ?????? ?????
    airdrop_amount = 5.0
    cursor.execute(
        "UPDATE users SET wallet_address = %s, balance = balance + %s, xp = xp + 50 WHERE user_id = %s",
        (wallet_addr, airdrop_amount, str(user_id))
    )
    
    # ????? ??????'??? ??????
    secure_transaction('SYSTEM', str(user_id), airdrop_amount, "TON_AIRDROP")
    
    conn.commit()
    conn.close()
    return True, airdrop_amount


