import os
from dotenv import load_dotenv

load_dotenv()

# טלגרם ושרת
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# מסד נתונים
DATABASE_URL = os.getenv("DATABASE_URL")

# משתני מוצר (מ-Railway)
PRICE_SH = os.getenv("PRICE_SH", "100")
TON_WALLET = os.getenv("TON_WALLET")
BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_ID = os.getenv("ADMIN_ID")
VIP_GROUP = os.getenv("PARTICIPANTS_GROUP_LINK", "https://t.me/osifeu")
REF_REWARD = os.getenv("REFERRAL_REWARD", "50")

# בינה מלאכותית
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
