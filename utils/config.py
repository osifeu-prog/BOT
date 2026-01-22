import os
from dotenv import load_dotenv
load_dotenv()

def safe_int(key, default):
    try: return int(float(os.getenv(key, default)))
    except: return int(default)

def safe_float(key, default):
    try: return float(os.getenv(key, default))
    except: return float(default)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
WIN_CHANCE = safe_float("WIN_CHANCE_PERCENT", 30.0) / 100
REFERRAL_REWARD = safe_int("REFERRAL_REWARD", 100)
ARCADE_COST = safe_int("PEEK_COST", 50)
