import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "osifeuprog")
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK")
TON_WALLET = os.getenv("TON_WALLET")
WIN_CHANCE = float(os.getenv("WIN_CHANCE_PERCENT", 30)) / 100
PORT = int(os.getenv("PORT", 8080))