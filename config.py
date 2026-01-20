import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", 500))
WIN_CHANCE = int(os.getenv("WIN_CHANCE_PERCENT", 80))
