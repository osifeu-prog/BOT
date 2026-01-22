import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = os.getenv("ADMIN_ID")
PORT = int(os.getenv("PORT", 8080))

# משתני פרויקט חדשים
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK", "https://t.me/your_group")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK", "https://t.me/your_test_group")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
TON_WALLET = os.getenv("TON_WALLET")