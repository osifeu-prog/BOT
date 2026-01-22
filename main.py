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

# --- ×¤×•× ×§×¦×™×•×ھ ×œ×™×‘×” ---
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

# --- ×ھ×¤×¨×™×ک×™×‌ ---
def main_menu(uid):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    role = get_user_role(uid)
    markup.add("ًں’³ ×¤×•×¨×ک×¤×•×œ×™×•", "ًں¤– ×،×•×›×ں AI", "ًں•¹ï¸ڈ ×گ×¨×§×™×™×“", "ًں›’ ×—× ×•×ھ", "ًںژپ ×‘×•× ×•×، ×™×•×‍×™", "ًں‘¥ ×”×–×‍×ں ×—×‘×¨×™×‌", "ًں“‹ ×‍×¦×‘ ×‍×¢×¨×›×ھ")
    if role >= 1: markup.add("ًں› ï¸ڈ ×¤×گ× ×œ × ×™×”×•×œ")
    return markup

def admin_panel(role):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("ًں“ٹ ×،×ک×ک×™×،×ک×™×§×”", "ًں“¢ ×©×™×“×•×¨ ×’×œ×•×‘×œ×™")
    if role >= 5: markup.add("ًں’° ×¢×¨×™×›×ھ ×™×ھ×¨×•×ھ", "ًں”‘ × ×™×”×•×œ ×”×¨×©×گ×•×ھ")
    if role >= 10: markup.add("âڑ™ï¸ڈ ×”×’×“×¨×•×ھ ×œ×™×‘×”", "ًں“‚ ×’×™×‘×•×™ DB")
    markup.add("ًں”™ ×—×–×¨×” ×œ×ھ×¤×¨×™×ک")
    return markup

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

# --- ×¤×§×•×“×•×ھ ×‍×¢×¨×›×ھ ---
@bot.message_handler(func=lambda m: m.text == "ًں“‹ ×‍×¦×‘ ×‍×¢×¨×›×ھ")
def system_status(message):
    status_report = (
        "ًں“ٹ **×“×•×— ×‍×¦×‘ ×‍×¢×¨×›×ھ - Diamond SaaS**\n"
        "------------------------------\n"
        "âœ… **×©×¨×ھ:** Railway Cloud - Active\n"
        "âœ… **×‍×،×“ × ×ھ×•× ×™×‌:** PostgreSQL - Connected\n"
        "âœ… **Websheet:** slh-nft.com - Live\n\n"
        "ًںڑ€ **×¤×™×ھ×•×— × ×•×›×—×™:** ×”×ک×‍×¢×ھ ×‍×¢×¨×›×ھ ×”×¨×©×گ×•×ھ 1-10\n"
        "ًں“… **×¢×“×›×•×ں ×گ×—×¨×•×ں:** 22/01/2026\n"
    )
    bot.reply_to(message, status_report, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "ًں› ï¸ڈ ×¤×گ× ×œ × ×™×”×•×œ")
def open_admin(message):
    role = get_user_role(message.from_user.id)
    if role < 1: return
    bot.send_message(message.chat.id, f"ًں‘‘ **×‘×¨×•×ڑ ×”×‘×گ ×œ×‍×¨×›×– ×”×©×œ×™×ک×”**\n×“×¨×’×ھ ×”×¨×©×گ×”: {role}", reply_markup=admin_panel(role))

@bot.message_handler(func=lambda m: m.text == "ًں“ٹ ×،×ک×ک×™×،×ک×™×§×”")
def stats(message):
    if get_user_role(message.from_user.id) < 1: return
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    cur.close(); conn.close()
    bot.reply_to(message, f"ًں“ˆ **× ×ھ×•× ×™ SaaS:**\n×‍×©×ھ×‍×©×™×‌ ×¨×©×•×‍×™×‌: {total}")

@bot.message_handler(func=lambda m: m.text == "ًں”™ ×—×–×¨×” ×œ×ھ×¤×¨×™×ک")
def back_home(message):
    bot.send_message(message.chat.id, "×—×–×¨×” ×œ×ھ×¤×¨×™×ک ×¨×گ×©×™", reply_markup=main_menu(message.from_user.id))

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "ًں’ژ **DIAMOND SUPREME**", reply_markup=main_menu(uid))

@app.on_event("startup")
def on_startup():
    patch_database()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

