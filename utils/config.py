import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# רק אתה יכול להשתמש בבוט
ALLOWED_USERS = [
    123456789  # ← להחליף ל-user_id שלך
]

DB_URL = os.getenv("DATABASE_URL")
