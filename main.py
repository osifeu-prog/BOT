# Version 4.0 - Auto-Recovery & Health System
import telebot, uvicorn, psycopg2, logging, os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DIAMOND_SHIELD")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# --- מנגנון הגנה לקבצים חסרים ---
def safe_read_html(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"❌ CRITICAL: {filename} IS MISSING!")
        return f"<html><body style='background:#020617;color:white;text-align:center;padding-top:50px;'><h1>🛠️ המערכת בשדרוג</h1><p>הקובץ {filename} חסר בשרת. פנה למנהל.</p></body></html>"

# --- נתיב בדיקת תקינות (Health Check) ---
@app.get("/health")
async def health_check():
    status = {"server": "online", "database": "unknown", "bot": "active"}
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        status["database"] = "connected ✅"
    except:
        status["database"] = "disconnected ❌"
    return status

@app.get("/wallet_page", response_class=HTMLResponse)
async def get_wallet():
    return safe_read_html("wallet.html")

@app.get("/games_page", response_class=HTMLResponse)
async def get_games():
    return safe_read_html("games.html")

# --- פקודת שחזור למנהל בלבד ---
@bot.message_handler(commands=['fix'])
def fix_system(message):
    if str(message.from_user.id) == "224223270": # ה-ID שלך
        try:
            bot.remove_webhook()
            bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
            bot.reply_to(message, "✅ המערכת אותחלה בהצלחה! ה-Webhook הוגדר מחדש.")
        except Exception as e:
            bot.reply_to(message, f"❌ שגיאה בשחזור: {e}")

# ... (שאר הפונקציות של main_menu ו-start נשארות כפי שהיו)
