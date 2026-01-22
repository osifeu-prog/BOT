import telebot, uvicorn, psycopg2, logging, os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# 1. ניהול לוגים וארכיטקטורה
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger("DIAMOND_SUPREME")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"
ADMIN_PW = "OSIF_DIAMOND_2026"

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- 2. נתיבי API ומיני-אפים ---

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
        return JSONResponse({"status": "error", "message": "סיסמה שגויה"}, status_code=403)
    
    try:
        conn = get_db(); cur = conn.cursor()
        # לוגיקה של העברה
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (int(data['amount']), str(data['sender_id'])))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (int(data['amount']), str(data['receiver_id'])))
        conn.commit(); cur.close(); conn.close()
        return {"status": "success"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

# --- 3. לוגיקה של הבוט (כפתורים ותגובות) ---

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    base_url = WEBHOOK_URL.split('/8106')[0]
    markup.add(
        KeyboardButton("💳 ארנק SUPREME", web_app=WebAppInfo(url=f"{base_url}/wallet_page")),
        KeyboardButton("🕹️ ארקייד גרפי", web_app=WebAppInfo(url=f"{base_url}/games_page"))
    )
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים")
    markup.add("👥 הזמן חברים", "📋 מצב מערכת")
    if str(uid) == ADMIN_ID: markup.add("👑 פאנל ניהול")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM**\nהמערכת פעילה. בחר פעולה:", reply_markup=main_menu(uid), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🏆 טבלת אלופים")
def leaderboard(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cur.fetchall()
    cur.close(); conn.close()
    msg = "🏆 **TOP 10 LEADERS**\n\n"
    for i, u in enumerate(top):
        msg += f"{i+1}. <code>{str(u[0])[:5]}***</code> — {u[1]:,} SLH\n"
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👥 הזמן חברים")
def invite(message):
    ref_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    bot.reply_to(message, f"🚀 **לינק הזמנה:**\n{ref_link}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📋 מצב מערכת")
def sys_status(message):
    bot.reply_to(message, "✅ **כל המערכות פועלות**\n📡 שרת: Railway\n🗄️ מסד נתונים: Connected\n🕹️ ארקייד: Online")

# פאנל אדמין בתוך הודעה אחת כדי לא להרוס כפתורים
@bot.message_handler(func=lambda m: m.text == "👑 פאנל ניהול" and str(m.from_user.id) == ADMIN_ID)
def admin_p(message):
    bot.send_message(message.chat.id, "🛠️ **ניהול מערכת**\n/fix - איפוס Webhook\n/stats - נתונים גלובליים")

@bot.message_handler(commands=['fix'])
def fix(message):
    if str(message.from_user.id) == ADMIN_ID:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
        bot.send_message(message.chat.id, "✅ Webhook Reset Done!")

# --- 4. שרת ו-Webhook ---

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
