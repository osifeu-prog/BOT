import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "osifeu_prog")
TON_WALLET = os.getenv("TON_WALLET")
PRICE_SH = os.getenv("PRICE_SH", "99")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "https://t.me/+2zNbLBrgrQkwZDhk")
PARTICIPANTS_GROUP_LINK = os.getenv("TEST_GROUP_LINK")
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 8080))
