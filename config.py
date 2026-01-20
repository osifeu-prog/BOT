import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK", "")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", "500"))
WIN_CHANCE_PERCENT = int(os.getenv("WIN_CHANCE_PERCENT", "80"))
PEEK_COST = int(os.getenv("PEEK_COST", "100"))
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN", "")
TON_WALLET = os.getenv("TON_WALLET", "")
TOKEN_PACKS = os.getenv("TOKEN_PACKS", "100:10,500:40,1000:70")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
