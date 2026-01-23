import os
from dotenv import load_dotenv
load_dotenv()

def safe_int(key, default):
    try: return int(float(os.getenv(key, default)))
    except: return int(default)

def safe_float(key, default):
    try: return float(os.getenv(key, default))
    except: return float(default)

# הגדרות בוט בסיסיות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")

# הגדרות שירות ו-SaaS (מה שגרם לשגיאה האחרונה)
BASE_URL = os.getenv("WEBHOOK_URL", "https://your-bot-link.railway.app")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@slh.com")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+972")
WHATSAPP_LINK = os.getenv("WHATSAPP_LINK", "https://wa.me/yourlink")

# הגדרות פיננסיות ומשחקים
DATABASE_URL = os.getenv("DATABASE_URL")
WIN_CHANCE = safe_float("WIN_CHANCE_PERCENT", 30.0) / 100
REFERRAL_REWARD = safe_int("REFERRAL_REWARD", 100)
ARCADE_COST = safe_int("PEEK_COST", 50)
PRICE_SH = safe_int("PRICE_SH", 10)
