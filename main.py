import telebot, uvicorn, psycopg2, logging, os
from fastapi import FastAPI, Request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    # בדיקה אם המשתמש הגיע דרך לינק הפניה
    ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
        logger.info(f"🆕 NEW USER JOINED: {uid}")
        if ref_id and ref_id != uid:
            cur.execute("UPDATE users SET balance = balance + 500 WHERE user_id = %s", (ref_id,))
            cur.execute("UPDATE users SET balance = balance + 200 WHERE user_id = %s", (uid,))
            logger.info(f"🎁 REFERRAL BONUS: {ref_id} invited {uid}")
    
    conn.commit(); cur.close(); conn.close()
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    wallet_url = f"https://slh-nft.com/wallet?id={uid}"
    markup.add(KeyboardButton("💎 ארנק SUPREME (גרפי)", web_app=WebAppInfo(url=wallet_url)))
    markup.add("📊 פורטפוליו", "👥 הזמן חברים", "🕹️ ארקייד", "📋 מצב מערכת")
    
    bot.send_message(message.chat.id, f"💎 **WELCOME TO DIAMOND SAAS**\nהארנק שלך מוכן עם 1,000 SLH מתנה!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "👥 הזמן חברים")
def send_ref_link(message):
    uid = message.from_user.id
    ref_link = f"https://t.me/{bot.get_me().username}?start={uid}"
    msg = f"🚀 **הזמן חברים והרווח כסף!**\n\nעל כל חבר שיצטרף דרך הלינק שלך:\n💰 אתה תקבל **500 SLH**\n🎁 החבר יקבל **200 SLH** בונוס!\n\nהלינק שלך:\n{ref_link}"
    bot.reply_to(message, msg, parse_mode="Markdown")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
