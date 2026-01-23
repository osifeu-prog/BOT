import os
from dotenv import load_dotenv

load_dotenv()

# משתנה מערכת קריטי שהיה חסר
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/"

# טעינת המשתנים מ-Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")

# משתני SaaS
REFERRAL_REWARD = float(os.getenv("REFERRAL_REWARD", 0.1))
WIN_CHANCE_PERCENT = int(os.getenv("WIN_CHANCE_PERCENT", 50))
PEEK_COST = float(os.getenv("PEEK_COST", 1.0))
PRICE_SH = float(os.getenv("PRICE_SH", 10.0))
LESSON_DB_PRICE = float(os.getenv("LESSON_DB_PRICE", 0.0))

# ארנקים וקישורים
TON_WALLET = os.getenv("TON_WALLET")
BOT_USERNAME = os.getenv("BOT_USERNAME")
PARTICIPANTS_GROUP_LINK = os.getenv("PARTICIPANTS_GROUP_LINK")
TEST_GROUP_LINK = os.getenv("TEST_GROUP_LINK")
