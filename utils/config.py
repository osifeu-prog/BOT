"""
config.py
=========
HE: קובץ קונפיגורציה מרכזי — טוקן, DB, Redis, פרטי קשר.
EN: Central configuration file — token, DB, Redis, contact details.
"""

import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

REDIS_URL = os.getenv("REDIS_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

OWNER_PHONE = "0584203384"
OWNER_EMAIL = "kaufmanungar@gmail.com"
OWNER_TELEGRAM = "@osifeu_prog"

SUPPORT_CONTACT_TEXT_HE = (
    f"📞 טלפון: {OWNER_PHONE}\n"
    f"📧 מייל: {OWNER_EMAIL}\n"
    f"טלגרם: {OWNER_TELEGRAM}"
)

SUPPORT_CONTACT_TEXT_EN = (
    f"📞 Phone: {OWNER_PHONE}\n"
    f"📧 Email: {OWNER_EMAIL}\n"
    f"Telegram: {OWNER_TELEGRAM}"
)
