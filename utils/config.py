import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

PRICE_SH = os.getenv("PRICE_SH", "50")  # מחיר בש"ח
TON_WALLET = os.getenv("TON_WALLET", "")
ZIP_LINK = os.getenv("ZIP_LINK", "")

DB_URL = os.getenv("DATABASE_URL")
