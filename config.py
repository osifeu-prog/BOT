"""
⚙️ קובץ הגדרות פשוט לפרוייקט
"""

import os
from dotenv import load_dotenv

load_dotenv()

# הגדרות בסיסיות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# הגדרות משחק
REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", "500"))
WIN_CHANCE_PERCENT = int(os.getenv("WIN_CHANCE_PERCENT", "80"))
PEEK_COST = int(os.getenv("PEEK_COST", "100"))

# תשלומים
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN", "")
TON_WALLET = os.getenv("TON_WALLET", "")

# קבוצות
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK", "")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "")

# חבילות מטבעות
TOKEN_PACKS = {}
packs_str = os.getenv("TOKEN_PACKS", "100:10,500:40,1000:70")
for pack in packs_str.split(","):
    if ":" in pack:
        amount, price = pack.split(":")
        TOKEN_PACKS[int(amount)] = int(price)

# AI (אופציונלי)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# הדפסת מידע debug
if __name__ == "__main__":
    print("⚙️ הגדרות הפרויקט:")
    print(f"✅ TELEGRAM_TOKEN: {'נטען' if TELEGRAM_TOKEN else '❌ חסר'}")
    print(f"👑 מנהלים: {len(ADMIN_IDS)}")
    print(f"🔗 Redis: {REDIS_URL}")
    print(f"🐞 Debug: {DEBUG_MODE}")
