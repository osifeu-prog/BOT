"""
db/connection.py
=================
אחראי על יצירת חיבור למסד הנתונים PostgreSQL.

כל פונקציה שעובדת מול DB:
- קוראת ל-get_conn()
- יוצרת cursor
- מריצה שאילתות
- סוגרת חיבור
"""

import psycopg2
from utils.config import DB_URL

def get_conn():
    """
    יוצר ומחזיר חיבור חדש למסד הנתונים.

    חשוב:
    - כל שימוש ב-DB צריך לסגור את החיבור בסוף.
    """
    return psycopg2.connect(DB_URL)
