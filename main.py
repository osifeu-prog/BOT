import telebot, uvicorn, psycopg2, logging, os
from fastapi import FastAPI, Request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

def get_user_role(uid):
    if str(uid) == str(ADMIN_ID): return 10
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT admin_level FROM users WHERE user_id = %s", (str(uid),))
        res = cur.fetchone()
        cur.close(); conn.close()
        return res[0] if res and res[0] is not None else 0
    except: return 0

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    role = get_user_role(uid)
    
    # מיני אפים נפרדים
    wallet_app = WebAppInfo(url="https://slh-nft.com/wallet") # דף הארנק
    site_app = WebAppInfo(url="https://slh-nft.com")        # דף הבית
    
    markup.add(
        KeyboardButton("💳 ארנק גרפי", web_app=wallet_app),
        KeyboardButton("🌐 אתר רשמי", web_app=site_app)
    )
    markup.add("📊 פורטפוליו", "🤖 סוכן AI", "🕹️ ארקייד", "🛒 חנות", "🎁 בונוס יומי", "👥 הזמן חברים", "📋 מצב מערכת")
    if role >= 1: markup.add("🛠️ פאנל ניהול")
    return markup

@bot.message_handler(commands=['all'])
def list_all_commands(message):
    role = get_user_role(message.from_user.id)
    cmd_text = (
        "📚 **מדריך פקודות Diamond Supreme**\n\n"
        "👤 **פקודות משתמש:**\n"
        "/start - ריענון הבוט\n"
        "/all - הצגת כל הפקודות\n"
        "/profile - הפרופיל שלי\n"
        "/ai - ניתוח שוק מהיר\n\n"
        "💸 **העברות:**\n"
        "/send [ID] [כמות] - העברת נקודות לחבר\n\n"
    )
    if role >= 1:
        cmd_text += (
            "🛡️ **פקודות אדמין:**\n"
            "/broadcast [טקסט] - הודעה לכולם\n"
            "/stats - נתוני מערכת\n"
        )
    if role == 10:
        cmd_text += "👑 /set_admin [ID] [1-10] - מינוי מנהל\n"
    
    bot.reply_to(message, cmd_text, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM**\nברוך הבא לממשק הניהול החדש.", reply_markup=main_menu(uid))

# פונקציות האדמין והמערכת נשארות כאן (broadcast, set_admin, etc.)
@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
