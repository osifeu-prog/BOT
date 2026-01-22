def log_leaderboard_status():
    try:
        conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 3")
        top = cur.fetchall()
        cur.close(); conn.close()
        msg = "\n" + "أ¢â€¢ع¯"*30 + "\nظ‹ع؛â€کâ€ک LEADERBOARD SNAPSHOT\n"
        for i, u in enumerate(top): msg += f" {i+1}. {u[0]} - {u[1]:,} SLH\n"
        msg += "أ¢â€¢ع¯"*30
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

# --- API ط£â€”ط¥â€œط£â€”ط¢آ©ط£â€”ط¥â€œط£â€”أ¢â€‍آ¢ط£â€”ط¢آ¤ط£â€”ط¹آ¾ ط£â€”ط¢آ ط£â€”ط¹آ¾ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬إ’ ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬ع©ط£â€”أ¢â€‍آ¢ط£â€”ط¢آ¦ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¢ ط£â€”ط¢آ¤ط£â€”ط¢آ¢ط£â€”أ¢â‚¬آ¢ط£â€”ط¥â€œط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾ ---

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
        return JSONResponse({"status": "error", "message": "ط£â€”ط¹آ¯ط£â€”أ¢â€‍آ¢ط£â€”ط¹ط› ط£â€”أ¢â‚¬ع†ط£â€”ط·إ’ط£â€”ط¢آ¤ط£â€”أ¢â€‍آ¢ط£â€”ط¢آ§ SLH"})
    
    # ط£â€”ط¥â€œط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬â„¢ط£â€”أ¢â€‍آ¢ط£â€”ط¢آ§ط£â€”ط¹آ¾ ط£â€”أ¢â‚¬â€œط£â€”أ¢â‚¬ط›ط£â€”أ¢â€‍آ¢ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬â€Œ: 30% ط£â€”ط·إ’ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬ط›ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â€‍آ¢ ط£â€”ط¥â€œط£â€”أ¢â‚¬â€œط£â€”أ¢â‚¬ط›ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾ ط£â€”أ¢â‚¬ع©-150 SLH
    win = random.random() < 0.3
    prize = 150 if win else 0
    new_balance = balance - cost + prize
    
    cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, uid))
    conn.commit(); cur.close(); conn.close()
    
    logger.info(f"ط¸â€¹ط¹ط›أ¢â‚¬آ¢ط¢آ¹ط£آ¯ط¢آ¸ط¹ث† ARCADE: User {uid} | Play: -{cost} | Win: +{prize} | New Bal: {new_balance}")
    return {"status": "success", "win": win, "prize": prize, "new_balance": new_balance}

@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    logger.info("ط¸â€¹ط¹ط›أ¢â‚¬إ“ط¢آ± HUB_OPENED: Interface requested")
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

# --- ط£â€”ط¢آ¤ط£â€”ط¢آ§ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬إ“ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾ ط£â€”أ¢â‚¬ع©ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ© ط£â€”أ¢â‚¬ع†ط£â€”ط¢آ¢ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬إ“ط£â€”أ¢â‚¬ط›ط£â€”ط¢آ ط£â€”أ¢â‚¬آ¢ط£â€”ط¹آ¾ ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("ط¸â€¹ط¹ط›أ¢â‚¬â„¢ط¹ع© SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("ط¸â€¹ط¹ط›أ¢â‚¬إ“ط¸آ¹ ط£â€”ط¢آ¤ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¨ط£â€”ط¹آ©ط£â€”ط¢آ¤ط£â€”أ¢â‚¬آ¢ط£â€”ط¥â€œط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬آ¢", "ط¸â€¹ط¹ط›ط¹ث†أ¢â‚¬آ  ط£â€”ط¹آ©ط£â€”أ¢â‚¬ع©ط£â€”ط¥â€œط£â€”ط¹آ¾ ط£â€”ط¹آ¯ط£â€”ط¥â€œط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ¤ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬إ’", "ط¸â€¹ط¹ط›أ¢â‚¬ع©ط¢آ¥ ط£â€”أ¢â‚¬â€Œط£â€”أ¢â‚¬â€œط£â€”أ¢â‚¬ع†ط£â€”ط¹ط› ط£â€”أ¢â‚¬â€‌ط£â€”أ¢â‚¬ع©ط£â€”ط¢آ¨ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬إ’", "ط¸â€¹ط¹ط›ط¹ع©ط¸آ¾ ط£â€”أ¢â‚¬ع©ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ ط£â€”أ¢â‚¬آ¢ط£â€”ط·إ’ ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬آ¢ط£â€”أ¢â‚¬ع†ط£â€”أ¢â€‍آ¢")
    if uid == ADMIN_ID: markup.add("ط¸â€¹ط¹ط›أ¢â‚¬ع©أ¢â‚¬ع© ط£â€”ط¢آ¤ط£â€”ط¹آ¯ط£â€”ط¢آ ط£â€”ط¥â€œ ط£â€”ط¢آ ط£â€”أ¢â€‍آ¢ط£â€”أ¢â‚¬â€Œط£â€”أ¢â‚¬آ¢ط£â€”ط¥â€œ")
    
    logger.info(f"ط¸â€¹ط¹ط›أ¢â‚¬آ أ¢â‚¬آ¢ START_CMD: User {uid} initialized menu")
    bot.send_message(message.chat.id, "ط¸â€¹ط¹ط›أ¢â‚¬â„¢ط¹ع© **DIAMOND SUPREME**\nط£â€”أ¢â‚¬â€Œط£â€”أ¢â‚¬ع†ط£â€”ط¢آ¢ط£â€”ط¢آ¨ط£â€”أ¢â‚¬ط›ط£â€”ط¹آ¾ ط£â€”أ¢â‚¬ع†ط£â€”ط·إ’ط£â€”أ¢â‚¬آ¢ط£â€”ط¢آ ط£â€”أ¢â‚¬ط›ط£â€”ط¢آ¨ط£â€”ط¢آ ط£â€”ط¹آ¾ ط£â€”ط¥â€œط£â€”أ¢â€‍آ¢ط£â€”ط¹آ¾ط£â€”ط¢آ¨ط£â€”أ¢â‚¬â€Œ ط£â€”ط¢آ©ط£â€”ط¥â€œط£â€”ط¹â€ک.", reply_markup=markup, parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def setup(): bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")



# --- Live Leaderboard Command for Users ---

@bot.message_handler(commands=['top'])
@bot.message_handler(func=lambda m: m.text == "🏆 טבלת אלופים")
def show_top_leaderboard(message):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
        top_ten = cur.fetchall()
        cur.close(); conn.close()

        msg = "👑 **DIAMOND SUPREME - TOP 10**\n"
        msg += "───────────────────\n"
        
        for i, user in enumerate(top_ten):
            # הסתרת חלק מה-ID לפרטיות, פרט לאדמין
            uid = str(user[0])
            display_id = uid if str(message.from_user.id) == ADMIN_ID else f"{uid[:4]}***{uid[-2:]}"
            
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔹"
            msg += f"{medal} **{display_id}** — {user[1]:,} SLH\n"
            
        msg += "───────────────────\n"
        msg += "🚀 *המשך לשחק כדי להגיע לטופ!*"
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        # קריאה ללוג הממורקר שביקשת קודם - כדי שגם אתה תראה את זה ברלוויי באותו רגע
        log_leaderboard_status()
        
    except Exception as e:
        logger.error(f"Error in leaderboard command: {e}")
        bot.send_message(message.chat.id, "❌ שגיאה בטעינת הטבלה.")
