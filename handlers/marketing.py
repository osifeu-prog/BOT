import psycopg2
from utils.config import DATABASE_URL

def generate_affiliate_link(user_id, bot_username):
    return f"https://t.me/{bot_username}?start={user_id}"

def process_referral(new_user_id, referrer_id):
    if not referrer_id or new_user_id == referrer_id:
        return
    conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()
    # בונוס למזמין (100 SLH)
    cur.execute("UPDATE users SET balance = balance + 100, xp = xp + 50 WHERE user_id = %s", (referrer_id,))
    # בונוס למוזמן (50 SLH)
    cur.execute("UPDATE users SET balance = balance + 50 WHERE user_id = %s", (new_user_id,))
    conn.commit(); cur.close(); conn.close()
