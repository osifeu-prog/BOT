import os
from dotenv import load_dotenv
load_dotenv()

# טלגרם - שימוש בשמות המדויקים מהפאנל שלך
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# מסדי נתונים (Railway מספק אותם אוטומטית)
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# ניהול וכסף
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")
PRICE_SH = os.getenv("PRICE_SH", "100")
TON_WALLET = os.getenv("TON_WALLET")
REF_REWARD = os.getenv("REFERRAL_REWARD", "50")
VIP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK")
