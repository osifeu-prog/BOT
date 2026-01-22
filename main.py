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

# --- פונקציית פרס אוטומטי (כל יום חמישי ב-22:00) ---
def give_weekly_prize():
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT user_id FROM users ORDER BY balance DESC LIMIT 1")
        winner = cur.fetchone()
        if winner:
            winner_id = winner[0]
            cur.execute("UPDATE users SET balance = balance + 5000 WHERE user_id = %s", (winner_id,))
            conn.commit()
            bot.send_message(winner_id, "🏆 מזל טוב! סיימת במקום הראשון השבוע וזכית ב-5,000 SLH!")
            logger.info(f"🏆 WEEKLY PRIZE GIVEN TO: {winner_id}")
        cur.close(); conn.close()
    except Exception as e:
        logger.error(f"Prize error: {e}")

# תפריט ראשי מתוקן
def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # שינוי ה-URL לשרת ה-Railway הנוכחי כדי למנוע 404
    wallet_url = f"{BASE_URL}/wallet_page"
    
    markup.add(KeyboardButton("💎 ארנק SUPREME (גרפי)", web_app=WebAppInfo(url=wallet_url)))
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים")
    markup.add("👥 הזמן חברים", "🕹️ ארקייד", "🛒 חנות", "📋 מצב מערכת")
    if get_user_role(uid) >= 1: markup.add("🛠️ פאנל ניהול")
    return markup

@app.get("/wallet_page", response_class=HTMLResponse)
async def get_wallet():
    with open("wallet.html", "r", encoding="utf-8") as f:
        return f.read()

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM**\nברוך הבא. הארנק והבונוסים שלך פעילים!", reply_markup=main_menu(uid))

@bot.message_handler(func=lambda m: m.text == "🏆 טבלת אלופים")
def show_leaderboard(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top = cur.fetchall()
    cur.close(); conn.close()
    msg = "🏆 **היכל התהילה** 🏆\n\n"
    for i, u in enumerate(top):
        msg += f"{i+1}. {str(u[0])[:5]}*** — {u[1]:,} SLH\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
    # הפעלת הפרס האוטומטי בשרשור נפרד
    def run_scheduler():
        schedule.every().thursday.at("22:00").do(give_weekly_prize)
        while True:
            schedule.run_pending()
            time.sleep(60)
    threading.Thread(target=run_scheduler, daemon=True).start()
