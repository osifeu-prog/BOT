def log_leaderboard_status():
    try:
        conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 3")
        top = cur.fetchall()
        cur.close(); conn.close()
        msg = "\n" + "═"*30 + "\n👑 LEADERBOARD SNAPSHOT\n"
        for i, u in enumerate(top): msg += f" {i+1}. {u[0]} - {u[1]:,} SLH\n"
        msg += "═"*30
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

# --- API ×œ×©×œ×™×¤×ھ × ×ھ×•× ×™×‌ ×•×‘×™×¦×•×¢ ×¤×¢×•×œ×•×ھ ---

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
        return JSONResponse({"status": "error", "message": "×گ×™×ں ×‍×،×¤×™×§ SLH"})
    
    # ×œ×•×’×™×§×ھ ×–×›×™×™×”: 30% ×،×™×›×•×™ ×œ×–×›×•×ھ ×‘-150 SLH
    win = random.random() < 0.3
    prize = 150 if win else 0
    new_balance = balance - cost + prize
    
    cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, uid))
    conn.commit(); cur.close(); conn.close()
    
    logger.info(f"ًں•¹ï¸ڈ ARCADE: User {uid} | Play: -{cost} | Win: +{prize} | New Bal: {new_balance}")
    return {"status": "success", "win": win, "prize": prize, "new_balance": new_balance}

@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    logger.info("ًں“± HUB_OPENED: Interface requested")
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

# --- ×¤×§×•×“×•×ھ ×‘×•×ک ×‍×¢×•×“×›× ×•×ھ ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("ًں’ژ SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("ًں“ٹ ×¤×•×¨×ک×¤×•×œ×™×•", "ًںڈ† ×ک×‘×œ×ھ ×گ×œ×•×¤×™×‌", "ًں‘¥ ×”×–×‍×ں ×—×‘×¨×™×‌", "ًںژپ ×‘×•× ×•×، ×™×•×‍×™")
    if uid == ADMIN_ID: markup.add("ًں‘‘ ×¤×گ× ×œ × ×™×”×•×œ")
    
    logger.info(f"ًں†• START_CMD: User {uid} initialized menu")
    bot.send_message(message.chat.id, "ًں’ژ **DIAMOND SUPREME**\n×”×‍×¢×¨×›×ھ ×‍×،×•× ×›×¨× ×ھ ×œ×™×ھ×¨×” ×©×œ×ڑ.", reply_markup=markup, parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def setup(): bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

