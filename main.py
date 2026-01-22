# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, logging, os, json, random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# לוגים שיראו הכל!
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger("DIAMOND_API")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# --- תיקון CORS - מאפשר למיני-אפ לדבר עם השרת ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db(): return psycopg2.connect(DATABASE_URL)

@app.get("/api/user_data/{uid}")
async def get_user_data(uid: str):
    logger.info(f"📡 API CALL: Fetching balance for {uid}")
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
        res = cur.fetchone()
        cur.close(); conn.close()
        balance = res[0] if res else 1000
        return {"balance": balance}
    except Exception as e:
        logger.error(f"❌ API ERROR (Data): {e}")
        return {"balance": 0}

@app.post("/api/play_arcade")
async def play_arcade(request: Request):
    try:
        data = await request.json()
        uid = str(data.get("user_id"))
        logger.info(f"🕹️ ARCADE ATTEMPT: User {uid}")
        
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
        balance = cur.fetchone()[0]
        
        if balance < 50:
            return JSONResponse({"status": "error", "message": "יתרה נמוכה מדי"})
        
        win = random.random() < 0.3
        prize = 150 if win else 0
        new_bal = balance - 50 + prize
        
        cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_bal, uid))
        conn.commit(); cur.close(); conn.close()
        
        logger.info(f"✅ ARCADE RESULT: {uid} | Win: {win} | New Balance: {new_bal}")
        return {"status": "success", "win": win, "prize": prize, "new_balance": new_bal}
    except Exception as e:
        logger.error(f"❌ API ERROR (Arcade): {e}")
        return JSONResponse({"status": "error", "message": "Server Error"})

@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    logger.info("📱 HUB ACCESS: Serving hub.html")
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    welcome = u"💎 **DIAMOND SUPREME SYSTEM**\n" + u"הממשק המאוחד מוכן עבורך."
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(u"💎 SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add(u"📊 פורטפוליו", u"🏆 טבלת אלופים", u"👥 הזמן חברים", u"🎁 בונוס יומי")
    bot.send_message(message.chat.id, welcome, reply_markup=markup, parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def setup(): bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
