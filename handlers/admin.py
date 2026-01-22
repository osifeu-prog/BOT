from utils.telegram import send_message
from db.connection import get_conn
from db.admins import is_admin

async def admin_handler(message, lang):
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    # אבטחה: אם המשתמש לא אדמין - מתעלמים
    if not is_admin(user_id):
        return

    # תפריט אדמין
    if text == "/admin":
        stats_msg = _get_stats()
        send_message(user_id, stats_msg)
        return

    # פקודות נוספות יכולות להיכנס כאן
    send_message(user_id, "פקודה לא מזוהה. נסה /admin")

def _get_stats():
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # ספירת משתמשים
        cur.execute("SELECT COUNT(*) FROM user_events WHERE event_type='message'")
        msgs = cur.fetchone()[0]
        
        # ספירת רוכשים (אם הטבלה קיימת)
        try:
            cur.execute("SELECT COUNT(*) FROM buyers")
            buyers = cur.fetchone()[0]
        except:
            buyers = 0
            
        cur.close()
        conn.close()
        
        return f"📊 **סטטיסטיקות בוט**\n\n💬 הודעות שנשלחו: {msgs}\n💰 רוכשים: {buyers}"
    except Exception as e:
        return f"שגיאה בשליפת נתונים: {e}"
