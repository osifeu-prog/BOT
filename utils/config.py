import os
from dotenv import load_dotenv

load_dotenv()

def get_env_int(key, default):
    val = os.getenv(key)
    if not val: return default
    try:
        # ממיר קודם לפלוט ואז לאינט כדי למנוע קריסה על "0.1"
        return int(float(val))
    except:
        return default

def get_env_float(key, default):
    val = os.getenv(key)
    if not val: return default
    try:
        return float(val)
    except:
        return default

# הגדרות ליבה
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# הגדרות מחוברות למשתני Railway - עכשיו חסינות לקריסה
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
WIN_CHANCE = get_env_float("WIN_CHANCE_PERCENT", 30.0) / 100
REFERRAL_REWARD = get_env_int("REFERRAL_REWARD", 100)
ARCADE_COST = get_env_int("PEEK_COST", 50)
