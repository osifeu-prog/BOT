import psycopg2, os
from utils.config import DATABASE_URL, BASE_URL, SUPPORT_PHONE

def get_market_insight(user_id):
    conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()
    cur.execute("SELECT entry FROM journal WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (user_id,))
    logs = cur.fetchall()
    cur.close(); conn.close()
    
    if not logs:
        return f"👋 ברוך הבא! אין לי עדיין נתונים עליך. בקר ב-{BASE_URL} או רשום כאן פעולות שוק."
    
    summary = " ".join([l[0] for l in logs])
    return f"🤖 **ניתוח סוכן חכם:**\nמזהה פעילות סביב: {summary[:50]}...\nהמלצה: בדוק את התיק שלך באתר הבית."
