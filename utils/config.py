import os

# טוקן של הבוט (מ‑Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# רשימת משתמשים מורשים (מ‑Railway)
# לדוגמה: ALLOWED_USERS="224223270,111111111"
allowed = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(x) for x in allowed.split(",") if x.strip().isdigit()]

# חיבור למסד הנתונים (מ‑Railway)
DB_URL = os.getenv("DATABASE_URL")
