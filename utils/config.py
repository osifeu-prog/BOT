import os
from dotenv import load_dotenv

load_dotenv()

# טלגרם
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# מסד נתונים
DATABASE_URL = os.getenv("DATABASE_URL")

# הגדרות TON
TONCENTER_API_KEY = os.getenv("TONCENTER_API_KEY")
TON_WALLET = os.getenv("TON_WALLET")
IS_TESTNET = True
TON_API_URL = "https://testnet.toncenter.com/api/v2/jsonRPC" if IS_TESTNET else "https://toncenter.com/api/v2/jsonRPC"

# משתני תאימות עבור saas.py וקוד קודם
BASE_URL = WEBHOOK_URL
SUPPORT_EMAIL = "support@slh.com"
SUPPORT_PHONE = "000000"
WHATSAPP_LINK = "https://wa.me/000000"
WIN_CHANCE = 50
WIN_CHANCE_PERCENT = 50
REFERRAL_REWARD = 0.1
PEEK_COST = 1.0
PRICE_SH = 10.0
LESSON_DB_PRICE = 0.0
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
