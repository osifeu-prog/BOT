"""
utils/config.py
================
קובץ הקונפיגורציה של הבוט.

מטרתו:
- לרכז את כל משתני הסביבה (ENV) במקום אחד.
- לאפשר שינוי הגדרות (מחיר, קישורים, טוקן וכו') בלי לגעת בקוד.
"""

import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

PRICE_SH = os.getenv("PRICE_SH", "254")
TON_WALLET = os.getenv("TON_WALLET", "")
ZIP_LINK = os.getenv("ZIP_LINK", "")

DB_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "")

START_PHOTO_URL = os.getenv(
    "START_PHOTO_URL",
    "https://raw.githubusercontent.com/osifeu-prog/BOT/main/assets/start.jpg"
)
