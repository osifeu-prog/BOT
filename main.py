import telebot, uvicorn, psycopg2, logging, os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# 1. × ×™×”×•×œ ×œ×•×’×™×‌ ×•×گ×¨×›×™×ک×§×ک×•×¨×”
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger("DIAMOND_SUPREME")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"
ADMIN_PW = "OSIF_DIAMOND_2026"

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- 2. × ×ھ×™×‘×™ API ×•×‍×™× ×™-×گ×¤×™×‌ ---

@app.get("/wallet_page", response_class=HTMLResponse)
async def get_wallet():
    try:
        with open("wallet.html", "r", encoding="utf-8") as f: return f.read()
    except: return "<h1>Wallet file missing</h1>"

@app.get("/games_page", response_class=HTMLResponse)
async def get_games():
    try:
        with open("games.html", "r", encoding="utf-8") as f: return f.read()
    except: return "<h1>Games file missing</h1>"

@app.post("/api/transfer")
async def transfer_funds(request: Request):
    data = await request.json()
    if data.get("password") != ADMIN_PW:
        return JSONResponse({"status": "error", "message": "×،×™×،×‍×” ×©×’×•×™×”"}, status_code=403)
    
    try:
        conn = get_db(); cur = conn.cursor()
        # ×œ×•×’×™×§×” ×©×œ ×”×¢×‘×¨×”
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (int(data['amount']), str(data['sender_id'])))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (int(data['amount']), str(data['receiver_id'])))
        conn.commit(); cur.close(); conn.close()
        return {"status": "success"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

# --- 3. ×œ×•×’×™×§×” ×©×œ ×”×‘×•×ک (×›×¤×ھ×•×¨×™×‌ ×•×ھ×’×•×‘×•×ھ) ---

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    base_url = WEBHOOK_URL.split('/8106')[0]
    markup.add(
        KeyboardButton("ًں’³ ×گ×¨× ×§ SUPREME", web_app=WebAppInfo(url=f"{base_url}/wallet_page")),
        KeyboardButton("ًں•¹ï¸ڈ ×گ×¨×§×™×™×“ ×’×¨×¤×™", web_app=WebAppInfo(url=f"{base_url}/games_page"))
    )
    markup.add("ًں“ٹ ×¤×•×¨×ک×¤×•×œ×™×•", "ًںڈ† ×ک×‘×œ×ھ ×گ×œ×•×¤×™×‌")
    markup.add("ًں‘¥ ×”×–×‍×ں ×—×‘×¨×™×‌", "ًں“‹ ×‍×¦×‘ ×‍×¢×¨×›×ھ")
    if str(uid) == ADMIN_ID: markup.add("ًں‘‘ ×¤×گ× ×œ × ×™×”×•×œ")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "ًں’ژ **DIAMOND SUPREME SYSTEM**\n×”×‍×¢×¨×›×ھ ×¤×¢×™×œ×”. ×‘×—×¨ ×¤×¢×•×œ×”:", reply_markup=main_menu(uid), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "ًںڈ† ×ک×‘×œ×ھ ×گ×œ×•×¤×™×‌")
def leaderboard(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cur.fetchall()
    cur.close(); conn.close()
    msg = "ًںڈ† **TOP 10 LEADERS**\n\n"
    for i, u in enumerate(top):
        msg += f"{i+1}. <code>{str(u[0])[:5]}***</code> â€” {u[1]:,} SLH\n"
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "ًں‘¥ ×”×–×‍×ں ×—×‘×¨×™×‌")
def invite(message):
    ref_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    bot.reply_to(message, f"ًںڑ€ **×œ×™× ×§ ×”×–×‍× ×”:**\n{ref_link}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "ًں“‹ ×‍×¦×‘ ×‍×¢×¨×›×ھ")
def sys_status(message):
    bot.reply_to(message, "âœ… **×›×œ ×”×‍×¢×¨×›×•×ھ ×¤×•×¢×œ×•×ھ**\nًں“، ×©×¨×ھ: Railway\nًں—„ï¸ڈ ×‍×،×“ × ×ھ×•× ×™×‌: Connected\nًں•¹ï¸ڈ ×گ×¨×§×™×™×“: Online")

# ×¤×گ× ×œ ×گ×“×‍×™×ں ×‘×ھ×•×ڑ ×”×•×“×¢×” ×گ×—×ھ ×›×“×™ ×œ×گ ×œ×”×¨×•×، ×›×¤×ھ×•×¨×™×‌
@bot.message_handler(func=lambda m: m.text == "ًں‘‘ ×¤×گ× ×œ × ×™×”×•×œ" and str(m.from_user.id) == ADMIN_ID)
def admin_p(message):
    bot.send_message(message.chat.id, "ًں› ï¸ڈ **× ×™×”×•×œ ×‍×¢×¨×›×ھ**\n/fix - ×گ×™×¤×•×، Webhook\n/stats - × ×ھ×•× ×™×‌ ×’×œ×•×‘×œ×™×™×‌")

@bot.message_handler(commands=['fix'])
def fix(message):
    if str(message.from_user.id) == ADMIN_ID:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
        bot.send_message(message.chat.id, "âœ… Webhook Reset Done!")

# --- 4. ×©×¨×ھ ×•-Webhook ---

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

# --- Daily Rewards & Quest System ---

@bot.message_handler(func=lambda m: m.text == "🎁 בונוס יומי")
def daily_bonus(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    
    # בדיקה מתי הייתה קבלת הבונוס האחרונה
    cur.execute("SELECT last_bonus FROM users WHERE user_id = %s", (uid,))
    last_bonus = cur.fetchone()[0]
    
    # לוגיקה פשוטה: פעם ב-24 שעות (אפשר לשכלל עם datetime)
    # לצורך ההדגמה, ניתן בונוס של 200 SLH
    cur.execute("UPDATE users SET balance = balance + 200, last_bonus = NOW() WHERE user_id = %s", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    bot.send_message(message.chat.id, "💰 **מזל טוב!**\nקיבלת בונוס יומי של 200 SLH.\nחזור מחר לבונוס גדול יותר!", parse_mode="HTML")

# שדרוג הפורטפוליו שיראה גם רווחים
@bot.message_handler(func=lambda m: m.text == "📊 פורטפוליו")
def portfolio(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
    bal = cur.fetchone()[0]
    cur.close(); conn.close()
    
    msg = f"📊 **DIAMOND PORTFOLIO**\n\n"
    msg += f"💰 יתרה: <code>{bal:,} SLH</code>\n"
    msg += f"📈 סטטוס: Diamond Holder\n"
    msg += f"🚀 שווי מוערך: {(bal * 0.12):.2f} USD" # סתם חישוב להמחשה
    bot.send_message(message.chat.id, msg, parse_mode="HTML")
