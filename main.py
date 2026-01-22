# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, logging, os, json, random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# הגדרת לוגים ברמת High-End
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DIAMOND_SYSTEM")

# שליפת משתנים מ-Railway עם ערכי ברירת מחדל בטיחותיים
WIN_CHANCE = float(os.getenv("WIN_CHANCE_PERCENT", 30)) / 100
REF_REWARD = int(os.getenv("REFERRAL_REWARD", 100))
ARCADE_COST = 50  # ניתן להוסיף כמשתנה ב-Railway

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- פונקציית ניטור לוגים ממורקרת ---
def log_event(category, message, success=True):
    color = "\033[92m" if success else "\033[91m" # Green / Red
    reset = "\033[0m"
    cyan = "\033[96m"
    print(f"{cyan}[{category}]{reset} {color}{message}{reset}")

# --- API INTEGRATION ---

@app.get("/api/user_data/{uid}")
async def get_user_data(uid: str):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
        res = cur.fetchone()
        cur.close(); conn.close()
        balance = res[0] if res else 1000
        log_event("📡 API_FETCH", f"User {uid} | Balance: {balance} SLH")
        return {"balance": balance}
    except Exception as e:
        log_event("❌ API_ERROR", str(e), False)
        return {"balance": 0}

@app.post("/api/play_arcade")
async def play_arcade(request: Request):
    try:
        data = await request.json()
        uid = str(data.get("user_id"))
        
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
        balance = cur.fetchone()[0]
        
        if balance < ARCADE_COST:
            return JSONResponse({"status": "error", "message": "יתרה נמוכה"})
        
        # שימוש במשתנה ה-WIN_CHANCE מה-Railway!
        win = random.random() < WIN_CHANCE
        prize = 150 if win else 0
        new_bal = balance - ARCADE_COST + prize
        
        cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_bal, uid))
        conn.commit(); cur.close(); conn.close()
        
        log_event("🕹️ ARCADE", f"User: {uid} | Bet: {ARCADE_COST} | Win: {win} ({prize} SLH) | Config Chance: {WIN_CHANCE*100}%")
        return {"status": "success", "win": win, "prize": prize, "new_balance": new_bal}
    except Exception as e:
        log_event("❌ ARCADE_FAIL", str(e), False)
        return JSONResponse({"status": "error", "message": "Server Error"})

@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    log_event("📱 HUB", "Serving Integrated UI")
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    welcome = f"💎 **DIAMOND SUPREME SYSTEM**\n\nשלום {message.from_user.first_name}!\nהמערכת מחוברת למסד הנתונים."
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("💎 SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים", "👥 הזמן חברים", "🎁 בונוס יומי")
    
    bot.send_message(message.chat.id, welcome, reply_markup=markup, parse_mode="HTML")
    log_event("🆕 USER_START", f"User {uid} entered system")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def setup(): 
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
    log_event("🚀 SYSTEM", "All Variable Connections Established")
