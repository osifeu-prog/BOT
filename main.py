import telebot, uvicorn, psycopg2, logging, os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

@app.get("/wallet_page", response_class=HTMLResponse)
async def get_wallet():
    with open("wallet.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/games_page", response_class=HTMLResponse)
async def get_games():
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
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "<b>💎 DIAMOND SYSTEM ACTIVE</b>\nברוך הבא לממשק היוקרה.", reply_markup=main_menu(uid), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🏆 טבלת אלופים")
def ldr(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cur.fetchall()
    cur.close(); conn.close()
    msg = "🏆 <b>TOP LEADERS</b>\n\n"
    for i, u in enumerate(top): msg += f"{i+1}. <code>{str(u[0])[:5]}***</code> — {u[1]:,} SLH\n"
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👥 הזמן חברים")
def inv(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    bot.reply_to(message, f"🚀 <b>לינק הזמנה:</b>\n<code>{link}</code>", parse_mode="HTML")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup(): bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
