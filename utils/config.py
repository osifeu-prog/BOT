import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsifShopbot")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OPENAI_KEY = os.getenv("OPENAI_KEY")
# התיקון הקריטי: הגדרת הפורט בצורה מפורשת
PORT = int(os.getenv("PORT", 8080)) 

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"