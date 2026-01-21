"""
utils/config.py
================
קובץ הקונפיגורציה של הבוט.

מטרתו:
- לרכז את כל משתני הסביבה (ENV) במקום אחד.
- לאפשר שינוי הגדרות (מחיר, קישורים, טוקן וכו') בלי לגעת בקוד.
"""

import os

# טוקן הבוט מטלגרם (מוגדר ב-Railway כ-TELEGRAM_TOKEN)
TOKEN = os.getenv("TELEGRAM_TOKEN")

# כתובת ה-API של טלגרם עבור הבוט הזה
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# מזהה המנהל הראשי (אתה)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# סיסמת מנהל — מי שמזין אותה דרך /admin הופך למנהל
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# מחיר הפרויקט בש"ח — מוצג למשתמשים
PRICE_SH = os.getenv("PRICE_SH", "254")

# ארנק TON לתשלום — מוצג למשתמשים
TON_WALLET = os.getenv("TON_WALLET", "")

# קישור ל-ZIP או ל-Release בגיטהאב
ZIP_LINK = os.getenv("ZIP_LINK", "https://github.com/osifeu-prog/BOT/releases/latest")

# כתובת מסד הנתונים PostgreSQL
DB_URL = os.getenv("DATABASE_URL")

# כתובת Redis — משמשת למשחק SLOTS ו-Leaderboard
REDIS_URL = os.getenv("REDIS_URL", "")

# כתובת התמונה שתוצג ב-/start
START_PHOTO_URL = os.getenv(
    "START_PHOTO_URL",
    "https://raw.githubusercontent.com/osifeu-prog/BOT/main/assets/start.jpg"
)
