"""
stats.py
========
HE: פונקציות סטטיסטיקה בסיסיות לאדמין.
EN: Basic statistics functions for admin.
"""

from db.connection import get_conn
from utils.edu_log import edu_step

def get_basic_stats():
    """
    מחזיר dict עם:
    - total_users (distinct user_id ב-user_events)
    - total_buyers
    - total_events
    - total_slots_games
    """
    edu_step(1, "Fetching basic stats.")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(DISTINCT user_id) FROM user_events")
    total_users = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM buyers")
    total_buyers = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM user_events")
    total_events = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM slots_history")
    total_slots_games = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    return {
        "total_users": total_users,
        "total_buyers": total_buyers,
        "total_events": total_events,
        "total_slots_games": total_slots_games,
    }

def get_recent_events(limit: int = 20):
    """
    מחזיר רשימת אירועים אחרונים.
    """
    edu_step(1, f"Fetching last {limit} events.")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, event_type, data, created_at
        FROM user_events
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
