import os
from dotenv import load_dotenv
load_dotenv()

# טלגרם
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ניהול
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "osifeu_prog")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShop_bot")

# קישורים וקבוצות
VIP_GROUP = os.getenv("PARTICIPANTS_GROUP_LINK", "https://t.me/+KLKB9-JdO85kNWJk")
TEST_GROUP = os.getenv("TEST_GROUP_LINK", "https://t.me/+5XzE0vQztaIzOTY0")

# מחירים וכלכלה
PRICE_SH = os.getenv("PRICE_SH", "99")
LESSON_PRICE = os.getenv("LESSON_DB_PRICE", "22")
REF_REWARD = os.getenv("REFERRAL_REWARD", "0.1")
TON_WALLET = os.getenv("TON_WALLET", "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp")
TOKEN_PACKS = os.getenv("TOKEN_PACKS", "💎 חבילת ארד: 10 | 💎 כסף: 25 | 💎 זהב: 70")

# משחקים
WIN_CHANCE = os.getenv("WIN_CHANCE_PERCENT", "70")

# מסדי נתונים
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
