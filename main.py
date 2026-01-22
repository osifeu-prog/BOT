import telebot, uvicorn, psycopg2, logging, os, schedule, time, threading
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

def get_user_role(uid):
    if str(uid) == str(ADMIN_ID): return 10
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT admin_level FROM users WHERE user_id = %s", (str(uid),))
        res = cur.fetchone()
        cur.close(); conn.close()
        return res[0] if res and res[0] is not None else 0
    except: return 0

@app.get("/wallet_page", response_class=HTMLResponse)
async def get_wallet():
    try:
        with open("wallet.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<html><body><h1>Wallet Temp Offline</h1></body></html>"

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    wallet_url = f"{WEBHOOK_URL.replace('/webhook', '')}/wallet_page"
    
    markup.add(KeyboardButton("💎 ארנק SUPREME (גרפי)", web_app=WebAppInfo(url=wallet_url)))
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים")
    markup.add("👥 הזמן חברים", "🕹️ ארקייד", "🛒 חנות", "📋 מצב מערכת")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "<b>💎 DIAMOND SUPREME SYSTEM</b>\nהארנק והבונוסים שלך פעילים!", reply_markup=main_menu(uid), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👥 הזמן חברים")
def send_ref_link(message):
    uid = message.from_user.id
    ref_link = f"https://t.me/{bot.get_me().username}?start={uid}"
    msg = f"🚀 <b>הזמן חברים והרווח!</b>\n\nהלינק האישי שלך:\n<code>{ref_link}</code>"
    bot.reply_to(message, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🏆 טבלת אלופים")
def show_leaderboard(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cur.fetchall()
    cur.close(); conn.close()
    msg = "🏆 <b>היכל התהילה</b> 🏆\n\n"
    for i, u in enumerate(top):
        msg += f"{i+1}. <code>{str(u[0])[:5]}***</code> — {u[1]:,} SLH\n"
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
