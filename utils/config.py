import os
from dotenv import load_dotenv

# טעינת משתנים מקובץ .env אם קיים (לוקאלי) או מהסביבה (Railway)
load_dotenv()

# --- משתני זהות ותמיכה (Hardcoded) ---
BASE_URL = "https://nft-israel.co.il"
SUPPORT_EMAIL = "kaufmanungar@gmail.com"
SUPPORT_PHONE = "0584203384"
WHATSAPP_LINK = f"https://wa.me/972{SUPPORT_PHONE[1:]}"

# --- משתני Railway (חובה שיהיו זהים לשמות בלוח הבקרה) ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ADMIN_ID = os.getenv('ADMIN_ID')
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WIN_CHANCE = int(os.getenv('WIN_CHANCE_PERCENT', 70))
BOT_USERNAME = os.getenv('BOT_USERNAME', 'OsifShop_bot')
TOKEN_PACKS = os.getenv('TOKEN_PACKS', 'חבילות טוקנים לא הוגדרו')
CRYPTO_PAY_TOKEN = os.getenv('CRYPTO_PAY_TOKEN')
TON_WALLET = os.getenv('TON_WALLET')

# כתובת ה-API של טלגרם
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
