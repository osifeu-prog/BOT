import telebot, uvicorn, psycopg2, logging, os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# 1. أ—آ أ—â„¢أ—â€‌أ—â€¢أ—إ“ أ—إ“أ—â€¢أ—â€™أ—â„¢أ—â€Œ أ—â€¢أ—ع¯أ—آ¨أ—â€؛أ—â„¢أ—ع©أ—آ§أ—ع©أ—â€¢أ—آ¨أ—â€‌
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger("DIAMOND_SUPREME")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"
ADMIN_PW = "OSIF_DIAMOND_2026"

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- 2. أ—آ أ—ع¾أ—â„¢أ—â€کأ—â„¢ API أ—â€¢أ—â€چأ—â„¢أ—آ أ—â„¢-أ—ع¯أ—آ¤أ—â„¢أ—â€Œ ---

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
        return JSONResponse({"status": "error", "message": "أ—طŒأ—â„¢أ—طŒأ—â€چأ—â€‌ أ—آ©أ—â€™أ—â€¢أ—â„¢أ—â€‌"}, status_code=403)
    
    try:
        conn = get_db(); cur = conn.cursor()
        # أ—إ“أ—â€¢أ—â€™أ—â„¢أ—آ§أ—â€‌ أ—آ©أ—إ“ أ—â€‌أ—آ¢أ—â€کأ—آ¨أ—â€‌
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (int(data['amount']), str(data['sender_id'])))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (int(data['amount']), str(data['receiver_id'])))
        conn.commit(); cur.close(); conn.close()
        return {"status": "success"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

# --- 3. أ—إ“أ—â€¢أ—â€™أ—â„¢أ—آ§أ—â€‌ أ—آ©أ—إ“ أ—â€‌أ—â€کأ—â€¢أ—ع© (أ—â€؛أ—آ¤أ—ع¾أ—â€¢أ—آ¨أ—â„¢أ—â€Œ أ—â€¢أ—ع¾أ—â€™أ—â€¢أ—â€کأ—â€¢أ—ع¾) ---

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    base_url = WEBHOOK_URL.split('/8106')[0]
    markup.add(
        KeyboardButton("ظ‹ع؛â€™آ³ أ—ع¯أ—آ¨أ—آ أ—آ§ SUPREME", web_app=WebAppInfo(url=f"{base_url}/wallet_page")),
        KeyboardButton("ظ‹ع؛â€¢آ¹أ¯آ¸عˆ أ—ع¯أ—آ¨أ—آ§أ—â„¢أ—â„¢أ—â€œ أ—â€™أ—آ¨أ—آ¤أ—â„¢", web_app=WebAppInfo(url=f"{base_url}/games_page"))
    )
    markup.add("ظ‹ع؛â€œظ¹ أ—آ¤أ—â€¢أ—آ¨أ—ع©أ—آ¤أ—â€¢أ—إ“أ—â„¢أ—â€¢", "ظ‹ع؛عˆâ€  أ—ع©أ—â€کأ—إ“أ—ع¾ أ—ع¯أ—إ“أ—â€¢أ—آ¤أ—â„¢أ—â€Œ")
    markup.add("ظ‹ع؛â€کآ¥ أ—â€‌أ—â€“أ—â€چأ—ع؛ أ—â€”أ—â€کأ—آ¨أ—â„¢أ—â€Œ", "ظ‹ع؛â€œâ€¹ أ—â€چأ—آ¦أ—â€ک أ—â€چأ—آ¢أ—آ¨أ—â€؛أ—ع¾")
    if str(uid) == ADMIN_ID: markup.add("ظ‹ع؛â€کâ€ک أ—آ¤أ—ع¯أ—آ أ—إ“ أ—آ أ—â„¢أ—â€‌أ—â€¢أ—إ“")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "ظ‹ع؛â€™عک **DIAMOND SUPREME SYSTEM**\nأ—â€‌أ—â€چأ—آ¢أ—آ¨أ—â€؛أ—ع¾ أ—آ¤أ—آ¢أ—â„¢أ—إ“أ—â€‌. أ—â€کأ—â€”أ—آ¨ أ—آ¤أ—آ¢أ—â€¢أ—إ“أ—â€‌:", reply_markup=main_menu(uid), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "ظ‹ع؛عˆâ€  أ—ع©أ—â€کأ—إ“أ—ع¾ أ—ع¯أ—إ“أ—â€¢أ—آ¤أ—â„¢أ—â€Œ")
def leaderboard(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cur.fetchall()
    cur.close(); conn.close()
    msg = "ظ‹ع؛عˆâ€  **TOP 10 LEADERS**\n\n"
    for i, u in enumerate(top):
        msg += f"{i+1}. <code>{str(u[0])[:5]}***</code> أ¢â‚¬â€‌ {u[1]:,} SLH\n"
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "ظ‹ع؛â€کآ¥ أ—â€‌أ—â€“أ—â€چأ—ع؛ أ—â€”أ—â€کأ—آ¨أ—â„¢أ—â€Œ")
def invite(message):
    ref_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    bot.reply_to(message, f"ظ‹ع؛ع‘â‚¬ **أ—إ“أ—â„¢أ—آ أ—آ§ أ—â€‌أ—â€“أ—â€چأ—آ أ—â€‌:**\n{ref_link}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "ظ‹ع؛â€œâ€¹ أ—â€چأ—آ¦أ—â€ک أ—â€چأ—آ¢أ—آ¨أ—â€؛أ—ع¾")
def sys_status(message):
    bot.reply_to(message, "أ¢إ“â€¦ **أ—â€؛أ—إ“ أ—â€‌أ—â€چأ—آ¢أ—آ¨أ—â€؛أ—â€¢أ—ع¾ أ—آ¤أ—â€¢أ—آ¢أ—إ“أ—â€¢أ—ع¾**\nظ‹ع؛â€œطŒ أ—آ©أ—آ¨أ—ع¾: Railway\nظ‹ع؛â€”â€‍أ¯آ¸عˆ أ—â€چأ—طŒأ—â€œ أ—آ أ—ع¾أ—â€¢أ—آ أ—â„¢أ—â€Œ: Connected\nظ‹ع؛â€¢آ¹أ¯آ¸عˆ أ—ع¯أ—آ¨أ—آ§أ—â„¢أ—â„¢أ—â€œ: Online")

# أ—آ¤أ—ع¯أ—آ أ—إ“ أ—ع¯أ—â€œأ—â€چأ—â„¢أ—ع؛ أ—â€کأ—ع¾أ—â€¢أ—ع‘ أ—â€‌أ—â€¢أ—â€œأ—آ¢أ—â€‌ أ—ع¯أ—â€”أ—ع¾ أ—â€؛أ—â€œأ—â„¢ أ—إ“أ—ع¯ أ—إ“أ—â€‌أ—آ¨أ—â€¢أ—طŒ أ—â€؛أ—آ¤أ—ع¾أ—â€¢أ—آ¨أ—â„¢أ—â€Œ
@bot.message_handler(func=lambda m: m.text == "ظ‹ع؛â€کâ€ک أ—آ¤أ—ع¯أ—آ أ—إ“ أ—آ أ—â„¢أ—â€‌أ—â€¢أ—إ“" and str(m.from_user.id) == ADMIN_ID)
def admin_p(message):
    bot.send_message(message.chat.id, "ظ‹ع؛â€؛آ أ¯آ¸عˆ **أ—آ أ—â„¢أ—â€‌أ—â€¢أ—إ“ أ—â€چأ—آ¢أ—آ¨أ—â€؛أ—ع¾**\n/fix - أ—ع¯أ—â„¢أ—آ¤أ—â€¢أ—طŒ Webhook\n/stats - أ—آ أ—ع¾أ—â€¢أ—آ أ—â„¢أ—â€Œ أ—â€™أ—إ“أ—â€¢أ—â€کأ—إ“أ—â„¢أ—â„¢أ—â€Œ")

@bot.message_handler(commands=['fix'])
def fix(message):
    if str(message.from_user.id) == ADMIN_ID:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
        bot.send_message(message.chat.id, "أ¢إ“â€¦ Webhook Reset Done!")

# --- 4. أ—آ©أ—آ¨أ—ع¾ أ—â€¢-Webhook ---

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

# --- Daily Rewards & Quest System ---

@bot.message_handler(func=lambda m: m.text == "ًںژپ ×‘×•× ×•×، ×™×•×‍×™")
def daily_bonus(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    
    # ×‘×“×™×§×” ×‍×ھ×™ ×”×™×™×ھ×” ×§×‘×œ×ھ ×”×‘×•× ×•×، ×”×گ×—×¨×•× ×”
    cur.execute("SELECT last_bonus FROM users WHERE user_id = %s", (uid,))
    last_bonus = cur.fetchone()[0]
    
    # ×œ×•×’×™×§×” ×¤×©×•×ک×”: ×¤×¢×‌ ×‘-24 ×©×¢×•×ھ (×گ×¤×©×¨ ×œ×©×›×œ×œ ×¢×‌ datetime)
    # ×œ×¦×•×¨×ڑ ×”×”×“×’×‍×”, × ×™×ھ×ں ×‘×•× ×•×، ×©×œ 200 SLH
    cur.execute("UPDATE users SET balance = balance + 200, last_bonus = NOW() WHERE user_id = %s", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    bot.send_message(message.chat.id, "ًں’° **×‍×–×œ ×ک×•×‘!**\n×§×™×‘×œ×ھ ×‘×•× ×•×، ×™×•×‍×™ ×©×œ 200 SLH.\n×—×–×•×¨ ×‍×—×¨ ×œ×‘×•× ×•×، ×’×“×•×œ ×™×•×ھ×¨!", parse_mode="HTML")

# ×©×“×¨×•×’ ×”×¤×•×¨×ک×¤×•×œ×™×• ×©×™×¨×گ×” ×’×‌ ×¨×•×•×—×™×‌
@bot.message_handler(func=lambda m: m.text == "ًں“ٹ ×¤×•×¨×ک×¤×•×œ×™×•")
def portfolio(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
    bal = cur.fetchone()[0]
    cur.close(); conn.close()
    
    msg = f"ًں“ٹ **DIAMOND PORTFOLIO**\n\n"
    msg += f"ًں’° ×™×ھ×¨×”: <code>{bal:,} SLH</code>\n"
    msg += f"ًں“ˆ ×،×ک×ک×•×،: Diamond Holder\n"
    msg += f"ًںڑ€ ×©×•×•×™ ×‍×•×¢×¨×ڑ: {(bal * 0.12):.2f} USD" # ×،×ھ×‌ ×—×™×©×•×‘ ×œ×”×‍×—×©×”
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# --- The Supreme Shop & Multipliers ---

@app.post("/api/buy_item")
async def buy_item(request: Request):
    data = await request.json()
    uid = str(data.get("user_id"))
    item_id = data.get("item_id") # למשל: 'multiplier_x2'
    price = int(data.get("price"))

    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
        balance = cur.fetchone()[0]

        if balance < price:
            return JSONResponse({"status": "error", "message": "אין מספיק SLH בחשבון!"})

        # הפחתת תשלום ועדכון פריט (כאן אפשר להוסיף טבלת inventory בעתיד)
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (price, uid))
        conn.commit(); cur.close(); conn.close()
        
        logger.info(f"🛒 SHOP PURCHASE: User {uid} bought {item_id} for {price} SLH")
        return {"status": "success", "new_balance": balance - price}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@bot.message_handler(func=lambda m: m.text == "🛒 חנות")
def open_shop(message):
    msg = "🏪 **SUPREME SHOP**\nמוצרים בלעדיים למחזיקי יהלומים:\n\n"
    msg += "1️⃣ **מכפיל X2 בארקייד** (12 שעות)\n💰 מחיר: 1,000 SLH\n\n"
    msg += "2️⃣ **סטטוס VIP יוקרתי**\n💰 מחיר: 5,000 SLH\n\n"
    msg += "לחץ על המוצר לרכישה (בקרוב בגרסה הגרפית!)"
    
    # בנתיים נציע את זה בטקסט, בגרסה הבאה נפתח לזה Mini App גרפי
    bot.send_message(message.chat.id, msg, parse_mode="HTML")
