import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "osifeu_prog")
TON_WALLET = os.getenv("TON_WALLET")
PRICE_SH = os.getenv("PRICE_SH", "99")
PORT = int(os.getenv("PORT", 8080))
