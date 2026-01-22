import os
from dotenv import load_dotenv

load_dotenv()

# --- משתני זהות מעודכנים ---
BASE_URL = "https://slh-nft.com"
SUPPORT_EMAIL = "kaufmanungar@gmail.com"
SUPPORT_PHONE = "0584203384"
WHATSAPP_LINK = "https://wa.me/+972584203384"

# --- משתני Railway ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ADMIN_ID = os.getenv('ADMIN_ID')
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WIN_CHANCE = int(os.getenv('WIN_CHANCE_PERCENT', 70))
BOT_USERNAME = os.getenv('BOT_USERNAME', 'OsifShop_bot')
TOKEN_PACKS = os.getenv('TOKEN_PACKS', 'חבילות טוקנים לא הוגדרו')
