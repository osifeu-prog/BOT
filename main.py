import telebot, uvicorn, psycopg2, logging
from fastapi import FastAPI, Request
from utils.config import (
    TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID, TOKEN_PACKS, 
    WIN_CHANCE, BOT_USERNAME, DATABASE_URL, BASE_URL, WHATSAPP_LINK, SUPPORT_EMAIL
)
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight
from handlers.saas import get_support_info, get_marketplace

# הגדרת לוגים מקצועית
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("DIAMOND_BOT")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db():
    return psycopg2.connect(DATABASE_URL)

def patch_database():
    logger.info("🛠️ Verifying Database Schema...")
    conn = get_db(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, balance INTEGER DEFAULT 100, xp INTEGER DEFAULT 0, rank TEXT DEFAULT 'Starter', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    cur.execute("CREATE TABLE IF NOT EXISTS journal (id SERIAL PRIMARY KEY, user_id TEXT, entry TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    conn.commit(); cur.close(); conn.close()
    logger.info("✅ Database Schema OK")

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💳 פורטפוליו & ארנק", "🤖 סוכן AI אסטרטגי", "🕹️ ארקייד Supreme", "🛒 חנות הבוטים", "🎁 הזמן חברים", "📞 תמיכה וקשר")
    return markup

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update_data = await request.body()
    update = telebot.types.Update.de_json(update_data.decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
    if not cur.fetchone():
        logger.info(f"🆕 NEW USER REGISTERED: {uid}")
        cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 100)", (uid,))
        conn.commit()
    else:
        logger.info(f"👋 EXISTING USER STARTED: {uid}")
    cur.close(); conn.close()
    bot.send_message(message.chat.id, f"💎 **DIAMOND SUPREME SYSTEM**\nברוך הבא לדור הבא.\n\n🌐 {BASE_URL}", reply_markup=main_menu())

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    msg = message.text.replace('/broadcast ', '')
    logger.warning(f"📣 ADMIN BROADCAST INITIATED: {msg[:30]}...")
    conn = get_db(); cur = conn.cursor(); cur.execute("SELECT user_id FROM users"); users = cur.fetchall()
    for u in users:
        try: bot.send_message(u[0], f"📢 **הודעה מערכת:**\n\n{msg}")
        except: pass
    bot.reply_to(message, "✅ נשלח!")

@bot.message_handler(commands=['add_cash'])
def add_cash(message):
    if str(message.from_user.id) != str(ADMIN_ID): return
    try:
        args = message.text.split()
        target, amount = args[1], args[2]
        cur = get_db().cursor(); cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, target))
        cur.connection.commit()
        logger.info(f"💰 ADMIN ADDED {amount} SLH TO {target}")
        bot.reply_to(message, "💰 עודכן!")
    except Exception as e:
        logger.error(f"❌ FAILED TO ADD CASH: {e}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    t, uid, cid = message.text, str(message.from_user.id), message.chat.id
    logger.info(f"📩 MSG FROM {uid}: {t}")
    
    if t == "💳 פורטפוליו & ארנק":
        cur = get_db().cursor(); cur.execute("SELECT balance, rank FROM users WHERE user_id = %s", (uid,))
        u = cur.fetchone()
        bot.send_message(cid, f"👤 **פרופיל**\n💰 יתרה: {u[0]} SLH\n🏅 דרגה: {u[1]}")
    elif t == "🤖 סוכן AI אסטרטגי":
        logger.info(f"🤖 AI AGENT CONSULTATION FOR {uid}")
        bot.send_message(cid, get_market_insight(uid))
    elif t == "🛒 חנות הבוטים": 
        bot.send_message(cid, f"🛒 **חנות**\n{TOKEN_PACKS}")
    elif t == "🕹️ ארקייד Supreme": 
        bot.send_message(cid, "🎰 הימור על 50 SLH:", reply_markup=telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("🎲 שחק", callback_data="p50")))
    elif t == "🎁 הזמן חברים": 
        bot.send_message(cid, f"🔗 https://t.me/{BOT_USERNAME}?start={uid}")
    elif t == "📞 תמיכה וקשר":
        bot.send_message(cid, f"📩 **צור קשר**\n\n🌐 {BASE_URL}\n💬 [ווטסאפ]({WHATSAPP_LINK})", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "p50")
def p50(c):
    logger.info(f"🎰 USER {c.from_user.id} PLAYING ARCADE")
    bot.send_message(c.message.chat.id, play_dice(c.message.chat.id, str(c.from_user.id), 50, 6))

@app.on_event("startup")
def on_startup():
    patch_database()
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
    logger.info(f"🚀 BOT DEPLOYED ON RAILWAY | ADMIN: {ADMIN_ID}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
