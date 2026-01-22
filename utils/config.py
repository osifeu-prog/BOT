import os
from dotenv import load_dotenv

load_dotenv()

# משתני ליבה
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# משתני מערכת (הגדרות מה-Railway UI)
ADMIN_ID = os.getenv("ADMIN_ID", "224223270")
WIN_CHANCE = float(os.getenv("WIN_CHANCE_PERCENT", 30)) / 100
REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", 100))
ARCADE_COST = int(os.getenv("PEEK_COST", 50))
