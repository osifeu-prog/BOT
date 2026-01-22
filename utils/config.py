import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "osifeu_prog")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
