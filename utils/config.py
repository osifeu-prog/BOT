import os
from dotenv import load_dotenv

# טעינת משתנים מקובץ .env אם קיים
load_dotenv()

# הגדרות טלגרם - שימוש בשמות משתנים תואמים ל-Error Logs
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# הגדרות בסיס נתונים
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# הגדרות מוצר ותשלומים
PRICE_SH = os.getenv("PRICE_SH", "100")
TON_WALLET = os.getenv("TON_WALLET", "")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
ZIP_LINK = os.getenv("ZIP_LINK", "")

# ניהול
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShopBot")
