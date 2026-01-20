import os
from dotenv import load_dotenv

load_dotenv()

# הטוקן - הכי חשוב!
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# אם הטוקן ריק, נסה לקבל ישירות (למקרה שיש בעיה ב-load_dotenv)
if not TELEGRAM_TOKEN:
    # אפשר גם להגדיר כאן ישירות ל-debugging
    # TELEGRAM_TOKEN = "הטוקן_האמיתי_כאן"
    pass

# הגדרות נוספות
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# הדפסה לצורך debug
if __name__ == "__main__":
    print(f"TELEGRAM_TOKEN loaded: {'✅' if TELEGRAM_TOKEN and TELEGRAM_TOKEN != 'YOUR_BOT_TOKEN_HERE' else '❌'}")
    print(f"Token starts with: {TELEGRAM_TOKEN[:10] if TELEGRAM_TOKEN else 'None'}...")
