import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "osifeu_prog")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShop_bot")

PRICE_SH = os.getenv("PRICE_SH", "99")
TON_WALLET = os.getenv("TON_WALLET", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")
TOKEN_PACKS = os.getenv("TOKEN_PACKS", "💎 חבילת ארד: 10 | 💎 כסף: 25 | 💎 זהב: 70")

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
