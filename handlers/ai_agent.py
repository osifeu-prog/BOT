import psycopg2
from utils.config import DATABASE_URL

def get_market_insight(user_id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT entry FROM journal WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (user_id,))
        entries = cur.fetchall()
        cur.close(); conn.close()
        
        if not entries:
            return "🤖 **ניתוח סוכן:**\nאין לי מספיק נתונים ביומן שלך עדיין. המשך לסחור ולתעד!"
        
        last_action = entries[0][0]
        return f"🤖 **ניתוח סוכן חכם:**\nמזהה פעילות אחרונה: '{last_action}'.\nהמלצה: המשך לעקוב אחר המגמה באתר הבית."
    except:
        return "🤖 הסוכן כרגע בלמידה, נסה שוב מאוחר יותר."
