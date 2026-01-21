"""
db/events.py
=============
אחראי על רישום כל פעולה של המשתמש בטבלת user_events.

למה זה חשוב?
- מעקב אחרי שימוש בבוט
- סטטיסטיקות
- ניתוח התנהגות משתמשים
- בסיס ל-Dashboard עתידי
"""

from db.connection import get_conn

def log_event(user_id, event_type, event_key, payload=None):
    """
    רושם אירוע חדש בטבלה user_events.

    user_id — מזהה המשתמש
    event_type — סוג האירוע (command / button / message)
    event_key — מה בדיוק קרה ("/start", "menu_buy" וכו')
    payload — מידע נוסף (למשל טקסט ההודעה)
    """
    conn = get_conn()
    cur = conn.cursor()

    # יצירת הטבלה אם היא לא קיימת
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            event_key TEXT NOT NULL,
            payload TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        '''
    )

    # הכנסת האירוע לטבלה
    cur.execute(
        "INSERT INTO user_events (user_id, event_type, event_key, payload) VALUES (%s, %s, %s, %s)",
        (user_id, event_type, event_key, payload)
    )

    conn.commit()
    cur.close()
    conn.close()
