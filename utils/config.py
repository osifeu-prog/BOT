import os
from dotenv import load_dotenv

load_dotenv()

# יסודות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

# תאימות לקבצים ישנים (saas.py, arcade.py וכו')
BASE_URL = WEBHOOK_URL
SUPPORT_EMAIL = "support@slh.com"
SUPPORT_PHONE = "000000"
WHATSAPP_LINK = "https://wa.me/000000"
WIN_CHANCE = int(os.getenv("WIN_CHANCE_PERCENT", 50))
WIN_CHANCE_PERCENT = WIN_CHANCE

# SaaS & Rewards
REFERRAL_REWARD = float(os.getenv("REFERRAL_REWARD", 0.1))
PEEK_COST = float(os.getenv("PEEK_COST", 1.0))
PRICE_SH = float(os.getenv("PRICE_SH", 10.0))
LESSON_DB_PRICE = float(os.getenv("LESSON_DB_PRICE", 0.0))

# Connections
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
