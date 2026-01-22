import os
from dotenv import load_dotenv
load_dotenv()

# Identity & Support
BASE_URL = "https://nft-israel.co.il"
SUPPORT_EMAIL = "kaufmanungar@gmail.com"
SUPPORT_PHONE = "0584203384"
WHATSAPP_LINK = f"https://wa.me/972{SUPPORT_PHONE[1:]}"

# Railway Variables (מושך ישירות מהרשימה שנתת)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WIN_CHANCE = int(os.getenv('WIN_CHANCE_PERCENT', 70))
CRYPTO_PAY_TOKEN = os.getenv('CRYPTO_PAY_TOKEN')
TON_WALLET = os.getenv('TON_WALLET')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'OsifShop_bot')
TOKEN_PACKS = os.getenv('TOKEN_PACKS')

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
