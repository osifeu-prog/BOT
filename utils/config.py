import os
from dotenv import load_dotenv

load_dotenv()

# טלגרם
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# מסד נתונים
DATABASE_URL = os.getenv("DATABASE_URL")

# הגדרות מוצר
PRICE_SH = os.getenv("PRICE_SH", "100")
TON_WALLET = os.getenv("TON_WALLET", "YOUR_TON_WALLET")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShopBot")
ADMIN_ID = os.getenv("ADMIN_ID") # אופציונלי
