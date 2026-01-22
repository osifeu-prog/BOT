import os
from dotenv import load_dotenv

load_dotenv()

# הגדרות המשתנים לפי Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShopbot")
ADMIN_ID = int(os.getenv("ADMIN_ID", "224223270"))
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 8080))

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"