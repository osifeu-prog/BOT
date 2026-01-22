import os

# טוקן וכתובת בסיס
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./diamond_bot.db")
PORT = int(os.getenv("PORT", 8080))

# אדמין
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

# קישורים וקבוצות
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK", "")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "")

# תשלומים וכלכלה
TON_WALLET = os.getenv("TON_WALLET", "Not Configured")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
REFERRAL_REWARD = os.getenv("REFERRAL_REWARD", 500)