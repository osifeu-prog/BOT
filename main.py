# Version 3.0 - Rich Logging & Fintech Core
import telebot, uvicorn, psycopg2, logging, os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# הגדרת לוגים מעוצבים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("DIAMOND_SERVER")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_PASSWORD = "OSIF_DIAMOND_2026"

def get_db(): return psycopg2.connect(DATABASE_URL)

@app.post("/api/transfer")
async def transfer_funds(request: Request):
    data = await request.json()
    sender_id = str(data.get("sender_id"))
    receiver_id = str(data.get("receiver_id"))
    amount = int(data.get("amount", 0))
    password = data.get("password")

    # לוג ניסיון העברה
    logger.info(f"💸 TRANSFER ATTEMPT: {sender_id} -> {receiver_id} | Amount: {amount}")

    if password != ADMIN_PASSWORD:
        logger.warning(f"⚠️ SECURITY ALERT: Wrong password attempt by {sender_id}!")
        return JSONResponse({"status": "error", "message": "סיסמה שגויה!"}, status_code=403)

    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (sender_id,))
        balance = cur.fetchone()[0]
        
        if balance < amount:
            logger.error(f"❌ TRANSFER FAILED: Insufficient funds for {sender_id}")
            return JSONResponse({"status": "error", "message": "יתרה נמוכה מדי!"})

        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, sender_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, receiver_id))
        conn.commit()
        
        logger.info(f"✅ TRANSFER SUCCESS: {amount} SLH moved to {receiver_id}. New balance for {sender_id}: {balance-amount}")
        
        try:
            bot.send_message(receiver_id, f"💰 קיבלת {amount:,} SLH!")
        except: pass
        
        cur.close(); conn.close()
        return {"status": "success", "new_balance": balance - amount}
    except Exception as e:
        logger.error(f"🔥 DATABASE ERROR: {str(e)}")
        return JSONResponse({"status": "error", "message": "שגיאת שרת"})

@app.get("/wallet_page", response_class=HTMLResponse)
async def get_wallet(request: Request):
    logger.info(f"📱 WALLET ACCESS: User requested graphical wallet")
    with open("wallet.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/games_page", response_class=HTMLResponse)
async def get_games():
    logger.info(f"🕹️ ARCADE ACCESS: User entered games area")
    with open("games.html", "r", encoding="utf-8") as f: return f.read()

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    base_url = WEBHOOK_URL.split('/8106')[0]
    markup.add(
        KeyboardButton("💳 ארנק SUPREME", web_app=WebAppInfo(url=f"{base_url}/wallet_page")),
        KeyboardButton("🕹️ ארקייד גרפי", web_app=WebAppInfo(url=f"{base_url}/games_page"))
    )
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים", "👥 הזמן חברים", "📋 מצב מערכת")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    logger.info(f"🆕 NEW SESSION: User {uid} started the bot")
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "<b>💎 DIAMOND SYSTEM</b>\nהמערכת מנטרת פעילות לביטחונך.", reply_markup=main_menu(uid), parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    logger.info("🚀 SYSTEM ONLINE: Diamond SaaS is up and running")
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
