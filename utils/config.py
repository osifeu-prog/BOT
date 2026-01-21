"""
utils/config.py
================
קובץ הקונפיגורציה של הבוט.

מטרתו:
- לרכז את כל משתני הסביבה (ENV) במקום אחד.
- לאפשר שינוי הגדרות (מחיר, קישורים, טוקן וכו') בלי לגעת בקוד.
"""
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

REDIS_URL = os.getenv("REDIS_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

OWNER_PHONE = "0584203384"
OWNER_EMAIL = "kaufmanungar@gmail.com"
SUPPORT_CONTACT_TEXT = (
    f"📞 טלפון: {OWNER_PHONE}\n"
    f"📧 מייל: {OWNER_EMAIL}\n"
    f"טלגרם: @osifeu_prog"
)
