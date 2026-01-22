import telebot, uvicorn, psycopg2, logging, datetime
from fastapi import FastAPI, Request
from utils.config import (
    TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID, TOKEN_PACKS, 
    WIN_CHANCE, BOT_USERNAME, DATABASE_URL, BASE_URL, WHATSAPP_LINK
)
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("DIAMOND_BOT")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db():
    return psycopg2.connect(DATABASE_URL)

def patch_database():
    conn = get_db(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, balance INTEGER DEFAULT 100, xp INTEGER DEFAULT 0, rank TEXT DEFAULT 'Starter', last_bonus TIMESTAMP DEFAULT NULL, referred_by TEXT DEFAULT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    cur.execute("CREATE TABLE IF NOT EXISTS journal (id SERIAL PRIMARY KEY, user_id TEXT, entry TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_bonus TIMESTAMP DEFAULT NULL;")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by TEXT DEFAULT NULL;")
    conn.commit(); cur.close(); conn.close()

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💳 פורטפוליו & ארנק", "🤖 סוכן AI אסטרטגי", "🕹️ ארקייד Supreme", "🛒 חנות הבוטים", "🎁 בונוס יומי", "👥 הזמן חברים", "📞 תמיכה וקשר")
    return markup

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    args = message.text.split()
    referrer = args[1] if len(args) > 1 else None
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
    if not cur.fetchone():
        # רישום משתמש חדש + בונוס למזמין
        cur.execute("INSERT INTO users (user_id, balance, referred_by) VALUES (%s, 100, %s)", (uid, referrer))
        if referrer:
            cur.execute("UPDATE users SET balance = balance + 50 WHERE user_id = %s", (referrer,))
            try: bot.send_message(referrer, "🎊 חבר נרשם דרכך! קיבלת 50 SLH בונוס.")
            except: pass
        conn.commit()
        bot.send_message(message.chat.id, "🎁 ברוך הבא! קיבלת 100 SLH מתנת הצטרפות.")
    cur.close(); conn.close()
    bot.send_message(message.chat.id, f"💎 **DIAMOND SUPREME**\nהמערכת פעילה עבורך.\n🌐 {BASE_URL}", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    t, uid, cid = message.text, str(message.from_user.id), message.chat.id
    
    if t == "🎁 בונוס יומי":
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT last_bonus FROM users WHERE user_id = %s", (uid,))
        last = cur.fetchone()[0]
        now = datetime.datetime.now()
        if last is None or (now - last).days >= 1:
            cur.execute("UPDATE users SET balance = balance + 50, last_bonus = %s WHERE user_id = %s", (now, uid))
            conn.commit()
            bot.send_message(cid, "✅ קיבלת 50 SLH בונוס יומי! חזור מחר.")
        else:
            bot.send_message(cid, "⏳ כבר אספת את הבונוס היום. חזור מחר!")
        cur.close(); conn.close()

    elif t == "👥 הזמן חברים":
        link = f"https://t.me/{BOT_USERNAME}?start={uid}"
        bot.send_message(cid, f"👥 **תוכנית השותפים**\n\nעל כל חבר שיצטרף דרך הלינק שלך, תקבל **50 SLH** מתנה!\n\n🔗 הלינק שלך:\n{link}")

    elif t == "💳 פורטפוליו & ארנק":
        cur = get_db().cursor(); cur.execute("SELECT balance, rank FROM users WHERE user_id = %s", (uid,))
        u = cur.fetchone(); bot.send_message(cid, f"👤 **פרופיל**\n💰 יתרה: {u[0]} SLH\n🏅 דרגה: {u[1]}")
    elif t == "🤖 סוכן AI אסטרטגי": bot.send_message(cid, get_market_insight(uid))
    elif t == "🕹️ ארקייד Supreme": bot.send_message(cid, "🎰 הימור 50 SLH:", reply_markup=telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("🎲 שחק", callback_data="p50")))
    elif t == "🛒 חנות הבוטים": bot.send_message(cid, f"🛒 **חנות**\n{TOKEN_PACKS}")
    elif t == "📞 תמיכה וקשר": bot.send_message(cid, f"📩 [צור קשר בווטסאפ]({WHATSAPP_LINK})", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "p50")
def p50(c): bot.send_message(c.message.chat.id, play_dice(c.message.chat.id, str(c.from_user.id), 50, 6))

@app.on_event("startup")
def on_startup():
    patch_database()
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
