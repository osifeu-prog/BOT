"""
config.py
=========
HE: קובץ קונפיגורציה מרכזי — קורא משתני סביבה מריילווי.
EN: Central configuration file — reads environment variables from Railway.
"""

import os

# HE: טוקן של הבוט מטלגרם (מ־Railway: TELEGRAM_TOKEN)
# EN: Telegram bot token (from Railway: TELEGRAM_TOKEN)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# HE: Webhook URL (מוגדר גם ב־BotFather וגם ב־Railway)
# EN: Webhook URL (set in BotFather and Railway)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# HE: חיבור למסד נתונים (Postgres)
# EN: Database connection string (Postgres)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# HE: חיבור ל־Redis (לשפה, התקדמות בקורס וכו')
# EN: Redis connection (language, course progress, etc.)
REDIS_URL = os.getenv("REDIS_URL", "")

# HE: מצב דיבוג — אם True, נדפיס לוגים חינוכיים צבעוניים.
# EN: Debug mode — if True, print colorful educational logs.
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# HE: פרטי אדמין (לממשק אדמין)
# EN: Admin details (for admin interface)
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "NFTY2026")

# HE: פרטי תשלום / קריפטו
# EN: Payment / crypto details
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN", "")
TON_WALLET = os.getenv("TON_WALLET", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")

# HE: לינק ל־ZIP של הפרויקט (לאחר רכישה)
# EN: Link to the project ZIP (after purchase)
ZIP_LINK = os.getenv("ZIP_LINK", "")

# HE: מחירים (בריילווי אפשר לשנות בלי לגעת בקוד)
# EN: Prices (can be changed in Railway without touching code)
PRICE_SH = float(os.getenv("PRICE_SH", "254"))  # מחיר הקורס/ערכת הסטארטאפ
LESSON_DB_PRICE = float(os.getenv("LESSON_DB_PRICE", "49"))  # לדוגמה: מחיר שיעור בודד
PEEK_COST = float(os.getenv("PEEK_COST", "10"))  # הצצה לעמוד נוסף
REFERRAL_REWARD = float(os.getenv("REFERRAL_REWARD", "20"))  # בונוס על הפניה

WIN_CHANCE_PERCENT = int(os.getenv("WIN_CHANCE_PERCENT", "20"))  # אחוז זכייה ב־SLOTS

TOKEN_PACKS = os.getenv("TOKEN_PACKS", "10,25,50")  # לדוגמה: חבילות טוקנים למשחק

# HE: קישורים לקבוצות / קהילה
# EN: Links to groups / community
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK", "")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "")

# HE: פרטי קשר שלך (מוטמעים בבוט ובדף הנחיתה)
# EN: Your contact details (embedded in bot and landing page)
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
