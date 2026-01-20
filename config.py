import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
BOT_USERNAME = os.getenv("BOT_USERNAME", "")

# ?????? ????
REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", "500"))
WIN_CHANCE_PERCENT = int(os.getenv("WIN_CHANCE_PERCENT", "80"))
PEEK_COST = int(os.getenv("PEEK_COST", "100"))

# ??????? (?????????)
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN", "")
TON_WALLET = os.getenv("TON_WALLET", "")

# ??????
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK", "")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "")

# ?????? ??????
TOKEN_PACKS = {}
packs_str = os.getenv("TOKEN_PACKS", "100:10,500:40,1000:70")
for pack in packs_str.split(","):
    if ":" in pack:
        amount, price = pack.split(":")
        TOKEN_PACKS[int(amount)] = int(price)
