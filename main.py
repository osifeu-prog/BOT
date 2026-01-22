import telebot, uvicorn, psycopg2, logging, datetime
from fastapi import FastAPI, Request
from utils.config import (
    TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID, TOKEN_PACKS, 
    WIN_CHANCE, BOT_USERNAME, DATABASE_URL, BASE_URL, WHATSAPP_LINK
)
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# --- פונקציות ליבה ---
def get_db(): return psycopg2.connect(DATABASE_URL)

def get_user_role(uid):
    if str(uid) == str(ADMIN_ID): return 10
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT admin_level FROM users WHERE user_id = %s", (str(uid),))
    res = cur.fetchone()
    cur.close(); conn.close()
    return res[0] if res else 0

def patch_database():
    conn = get_db(); cur = conn.cursor()
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS admin_level INTEGER DEFAULT 0;")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS status_updates TEXT DEFAULT 'System Initialized';")
    conn.commit(); cur.close(); conn.close()

# --- תפריטים ---
def main_menu(uid):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    role = get_user_role(uid)
    markup.add("💳 פורטפוליו", "🤖 סוכן AI", "🕹️ ארקייד", "🛒 חנות", "🎁 בונוס יומי", "👥 הזמן חברים", "📋 מצב מערכת")
    if role >= 1: markup.add("🛠️ פאנל ניהול")
    return markup

def admin_panel(role):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 סטטיסטיקה", "📢 שידור גלובלי")
    if role >= 5: markup.add("💰 עריכת יתרות", "🔑 ניהול הרשאות")
    if role >= 10: markup.add("⚙️ הגדרות ליבה", "📂 גיבוי DB")
    markup.add("🔙 חזרה לתפריט")
    return markup

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

# --- פקודות מערכת ---
@bot.message_handler(func=lambda m: m.text == "📋 מצב מערכת")
def system_status(message):
    status_report = (
        "📊 **דוח מצב מערכת - Diamond SaaS**\n"
        "------------------------------\n"
        "✅ **שרת:** Railway Cloud - Active\n"
        "✅ **מסד נתונים:** PostgreSQL - Connected\n"
        "✅ **Websheet:** slh-nft.com - Live\n\n"
        "🚀 **פיתוח נוכחי:** הטמעת מערכת הרשאות 1-10\n"
        "📅 **עדכון אחרון:** 22/01/2026\n"
    )
    bot.reply_to(message, status_report, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛠️ פאנל ניהול")
def open_admin(message):
    role = get_user_role(message.from_user.id)
    if role < 1: return
    bot.send_message(message.chat.id, f"👑 **ברוך הבא למרכז השליטה**\nדרגת הרשאה: {role}", reply_markup=admin_panel(role))

@bot.message_handler(func=lambda m: m.text == "📊 סטטיסטיקה")
def stats(message):
    if get_user_role(message.from_user.id) < 1: return
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    cur.close(); conn.close()
    bot.reply_to(message, f"📈 **נתוני SaaS:**\nמשתמשים רשומים: {total}")

@bot.message_handler(func=lambda m: m.text == "🔙 חזרה לתפריט")
def back_home(message):
    bot.send_message(message.chat.id, "חזרה לתפריט ראשי", reply_markup=main_menu(message.from_user.id))

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME**", reply_markup=main_menu(uid))

@app.on_event("startup")
def on_startup():
    patch_database()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
