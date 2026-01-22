import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
PRICE_SH = os.getenv("PRICE_SH", "100")
TON_WALLET = os.getenv("TON_WALLET")
BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_ID = os.getenv("ADMIN_ID")
REF_REWARD = os.getenv("REFERRAL_REWARD", "50")
