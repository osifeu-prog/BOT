import os

# טוקן של הבוט
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# מזהה המנהל הראשי (רק אתה)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# סיסמת מנהל — משתמשים שיזינו אותה יהפכו למנהלים
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# מחיר בש"ח
PRICE_SH = os.getenv("PRICE_SH", "50")

# ארנק TON לתשלום
TON_WALLET = os.getenv("TON_WALLET", "")

# קישור ל‑ZIP
ZIP_LINK = os.getenv("ZIP_LINK", "")

# מסד נתונים
DB_URL = os.getenv("DATABASE_URL")
