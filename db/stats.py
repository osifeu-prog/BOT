from db.connection import get_conn

def get_admin_stats():
    conn = get_conn()
    cur = conn.cursor()
    # ספירת משתמשים
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    # סכום מאזנים (כסף במערכת)
    cur.execute("SELECT SUM(balance) FROM users")
    total_balance = cur.fetchone()[0] or 0
    cur.close()
    conn.close()
    return total_users, total_balance
