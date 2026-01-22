import telebot, uvicorn, psycopg2, logging, os
from fastapi import FastAPI, Request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# הגדרת לוגים שיפיעו ב-Railway
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # כפתור המיני אפ - פותח את האתר שלך בתוך טלגרם
    web_app = WebAppInfo(url="https://slh-nft.com")
    
    markup.add(
        KeyboardButton("💳 ארנק הדיאמונד (Web)", web_app=web_app),
        KeyboardButton("📊 פורטפוליו טקסט")
    )
    markup.add("🤖 סוכן AI", "🕹️ ארקייד", "🛒 חנות", "🎁 בונוס יומי", "👥 הזמן חברים", "📋 מצב מערכת")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    logger.info(f"🚀 USER STARTED: {uid}")
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM**\nברוך הבא לממשק הניהול החדש.", reply_markup=main_menu(uid))

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    update = telebot.types.Update.de_json(body)
    bot.process_new_updates([update])
    return "ok"

# שאר הפונקציות (העברה, ארקייד וכו') נשארות כפי שהן
