# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, logging, os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# הגדרת לוגים עשירים ל-Railway
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("DIAMOND_HUB")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"
ADMIN_PW = "OSIF_DIAMOND_2026"

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- נתיבי API וממשק ---

@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    logger.info("📱 HUB ACCESS: User opened the integrated interface")
    try:
        with open("hub.html", "r", encoding="utf-8") as f: return f.read()
    except Exception as e:
        logger.error(f"❌ FILE ERROR: hub.html missing! {e}")
        return "<h1>HUB FILE MISSING</h1>"

@app.post("/api/transfer")
async def transfer_funds(request: Request):
    data = await request.json()
    sid, rid, amt, pw = str(data.get("sender_id")), str(data.get("receiver_id")), int(data.get("amount", 0)), data.get("password")
    
    logger.info(f"💸 TRANSFER ATTEMPT: {sid} -> {rid} | Amount: {amt}")
    
    if pw != ADMIN_PW:
        logger.warning(f"⚠️ AUTH FAILED: Invalid PIN from {sid}")
        return JSONResponse({"status": "error", "message": "סיסמה שגויה"}, status_code=403)

    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (sid,))
        if cur.fetchone()[0] < amt:
            return JSONResponse({"status": "error", "message": "יתרה נמוכה מדי"})
        
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amt, sid))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amt, rid))
        conn.commit(); cur.close(); conn.close()
        
        logger.info(f"✅ SUCCESS: {amt} SLH transferred to {rid}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"🔥 DB ERROR: {e}")
        return JSONResponse({"status": "error", "message": "שגיאת שרת"})

# --- פקודות בוט ---

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup.add(KeyboardButton("💎 SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים", "👥 הזמן חברים", "🎁 בונוס יומי")
    if str(uid) == ADMIN_ID: markup.add("👑 פאנל ניהול")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    logger.info(f"🆕 SESSION: User {uid} started the bot")
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM**\nהממשק המאוחד מוכן עבורך.", reply_markup=main_menu(uid), parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def startup():
    logger.info("🚀 SYSTEM ONLINE: Diamond Hub is ready")
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
