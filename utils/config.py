import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShopbot")
ADMIN_ID = int(os.getenv("ADMIN_ID", "224223270")) # וודא שזה ה-ID שלך
OPENAI_KEY = os.getenv("OPENAI_KEY")
PORT = int(os.getenv("PORT", 8080))
DATABASE_URL = os.getenv("DATABASE_URL") # הכרחי להתחברות ל-DB

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"