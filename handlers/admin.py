from utils.telegram import send_message
from db.admins import is_admin
from db.connection import get_conn

async def admin_handler(message):
    user_id = message["from"]["id"]
    if not is_admin(user_id):
        return
        
    # שליפת סטטיסטיקה
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]
        conn.close()
        send_message(user_id, f"📊 משתמשים רשומים: {users}")
    except:
        send_message(user_id, "שגיאה בשליפת נתונים")
