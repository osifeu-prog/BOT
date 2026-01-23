import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
ADMIN_ID = os.getenv("ADMIN_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# SaaS Variables - תמיכה בשמות כפולים למניעת קריסה
REFERRAL_REWARD = float(os.getenv("REFERRAL_REWARD", 0.1))
WIN_CHANCE_PERCENT = int(os.getenv("WIN_CHANCE_PERCENT", 50))
WIN_CHANCE = WIN_CHANCE_PERCENT  # תאימות ל-arcade.py
PEEK_COST = float(os.getenv("PEEK_COST", 1.0))
PRICE_SH = float(os.getenv("PRICE_SH", 10.0))

# Connections
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
