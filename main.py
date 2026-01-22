def log_leaderboard_status():
    try:
        conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 3")
        top = cur.fetchall()
        cur.close(); conn.close()
        msg = "\n" + "â•گ"*30 + "\nًں‘‘ LEADERBOARD SNAPSHOT\n"
        for i, u in enumerate(top): msg += f" {i+1}. {u[0]} - {u[1]:,} SLH\n"
        msg += "â•گ"*30
        print(msg)
    except: pass
# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, logging, os, json, random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("DIAMOND_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"
ADMIN_PW = "OSIF_DIAMOND_2026"

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- API أ—إ“أ—آ©أ—إ“أ—â„¢أ—آ¤أ—ع¾ أ—آ أ—ع¾أ—â€¢أ—آ أ—â„¢أ—â€Œ أ—â€¢أ—â€کأ—â„¢أ—آ¦أ—â€¢أ—آ¢ أ—آ¤أ—آ¢أ—â€¢أ—إ“أ—â€¢أ—ع¾ ---

@app.get("/api/user_data/{uid}")
async def get_user_data(uid: str):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
    res = cur.fetchone()
    cur.close(); conn.close()
    if res:
        return {"balance": res[0]}
    return {"balance": 0}

@app.post("/api/play_arcade")
async def play_arcade(request: Request):
    data = await request.json()
    uid = str(data.get("user_id"))
    cost = 50
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
    balance = cur.fetchone()[0]
    
    if balance < cost:
        return JSONResponse({"status": "error", "message": "أ—ع¯أ—â„¢أ—ع؛ أ—â€چأ—طŒأ—آ¤أ—â„¢أ—آ§ SLH"})
    
    # أ—إ“أ—â€¢أ—â€™أ—â„¢أ—آ§أ—ع¾ أ—â€“أ—â€؛أ—â„¢أ—â„¢أ—â€‌: 30% أ—طŒأ—â„¢أ—â€؛أ—â€¢أ—â„¢ أ—إ“أ—â€“أ—â€؛أ—â€¢أ—ع¾ أ—â€ک-150 SLH
    win = random.random() < 0.3
    prize = 150 if win else 0
    new_balance = balance - cost + prize
    
    cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, uid))
    conn.commit(); cur.close(); conn.close()
    
    logger.info(f"ظ‹ع؛â€¢آ¹أ¯آ¸عˆ ARCADE: User {uid} | Play: -{cost} | Win: +{prize} | New Bal: {new_balance}")
    return {"status": "success", "win": win, "prize": prize, "new_balance": new_balance}

@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    logger.info("ظ‹ع؛â€œآ± HUB_OPENED: Interface requested")
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

# --- أ—آ¤أ—آ§أ—â€¢أ—â€œأ—â€¢أ—ع¾ أ—â€کأ—â€¢أ—ع© أ—â€چأ—آ¢أ—â€¢أ—â€œأ—â€؛أ—آ أ—â€¢أ—ع¾ ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("ظ‹ع؛â€™عک SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("ظ‹ع؛â€œظ¹ أ—آ¤أ—â€¢أ—آ¨أ—ع©أ—آ¤أ—â€¢أ—إ“أ—â„¢أ—â€¢", "ظ‹ع؛عˆâ€  أ—ع©أ—â€کأ—إ“أ—ع¾ أ—ع¯أ—إ“أ—â€¢أ—آ¤أ—â„¢أ—â€Œ", "ظ‹ع؛â€کآ¥ أ—â€‌أ—â€“أ—â€چأ—ع؛ أ—â€”أ—â€کأ—آ¨أ—â„¢أ—â€Œ", "ظ‹ع؛عکظ¾ أ—â€کأ—â€¢أ—آ أ—â€¢أ—طŒ أ—â„¢أ—â€¢أ—â€چأ—â„¢")
    if uid == ADMIN_ID: markup.add("ظ‹ع؛â€کâ€ک أ—آ¤أ—ع¯أ—آ أ—إ“ أ—آ أ—â„¢أ—â€‌أ—â€¢أ—إ“")
    
    logger.info(f"ظ‹ع؛â€ â€¢ START_CMD: User {uid} initialized menu")
    bot.send_message(message.chat.id, "ظ‹ع؛â€™عک **DIAMOND SUPREME**\nأ—â€‌أ—â€چأ—آ¢أ—آ¨أ—â€؛أ—ع¾ أ—â€چأ—طŒأ—â€¢أ—آ أ—â€؛أ—آ¨أ—آ أ—ع¾ أ—إ“أ—â„¢أ—ع¾أ—آ¨أ—â€‌ أ—آ©أ—إ“أ—ع‘.", reply_markup=markup, parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def setup(): bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")


