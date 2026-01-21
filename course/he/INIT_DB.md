# 🗄️ יצירת מסד נתונים אוטומטית – init_db.py

בשיעור הזה נלמד איך לגרום למערכת שלך ליצור את כל הטבלאות הדרושות **אוטומטית**, בכל פעם שהבוט עולה.  
זה פותר בעיות נפוצות, חוסך זמן, ומונע תקלות כמו "עמודה חסרה" או "טבלה לא קיימת".

---

## למה בכלל צריך init_db.py?

בשלבים מוקדמים של פיתוח:

- מוחקים ומתקינים מחדש את ה־DB
- מבנה הטבלאות משתנה
- תלמידים עושים טעויות
- Railway לא יוצר טבלאות לבד
- PostgreSQL לא “מנחש” מה צריך

לכן, אנחנו יוצרים סקריפט שמוודא:

- שכל הטבלאות קיימות
- שכל העמודות קיימות
- שהמערכת מוכנה לעבודה בכל Deploy

זה הופך את הפרויקט ל־**Self Healing**.

---

## איך זה עובד?

הסקריפט:

1. מתחבר ל־PostgreSQL דרך `DATABASE_URL`
2. עובר על רשימת טבלאות מוגדרת מראש
3. מריץ `CREATE TABLE IF NOT EXISTS`
4. מבטיח שהכול קיים לפני שהבוט מתחיל לעבוד

---

## קוד מלא של init_db.py

```python
import psycopg2
from utils.config import DATABASE_URL

TABLES = {
    "user_events": """
        CREATE TABLE IF NOT EXISTS user_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """,

    "admins": """
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY
        );
    """,

    "buyers": """
        CREATE TABLE IF NOT EXISTS buyers (
            user_id BIGINT PRIMARY KEY,
            purchased_at TIMESTAMP DEFAULT NOW()
        );
    """,

    "slots_history": """
        CREATE TABLE IF NOT EXISTS slots_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """
}


def init_db():
    print("🔧 Initializing database...")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for name, ddl in TABLES.items():
        print(f"📌 Ensuring table exists: {name}")
        cur.execute(ddl)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Database initialization complete.")


if __name__ == "__main__":
    init_db()
