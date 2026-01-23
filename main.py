# -*- coding: utf-8 -*-
import telebot, os, uvicorn, logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from utils.config import *
from handlers import wallet_logic
from db.connection import init_db, get_conn

# הגדרת לוגים שיופיעו ב-Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 SLH OS System starting up...")
    try:
        # בדיקת חיבור ל-DB בזמן עליה
        conn = get_conn()
        conn.close()
        logger.info("✅ Database connection verified!")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

@app.get("/gui/wallet", response_class=HTMLResponse)
async def wallet_gui(user_id: str):
    logger.info(f"📱 Wallet GUI requested for user: {user_id}")
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    return f\"\"\"
    <html><body style='background:#000;color:#fff;font-family:sans-serif;text-align:center;padding:50px;'>
        <h1 style='color:#0088cc;'>SLH Wallet</h1>
        <div style='font-size:40px;'>{balance} SLH</div>
        <p>Rank: {rank} | XP: {xp}</p>
        <button onclick='window.Telegram.WebApp.close()' style='padding:10px 20px;border-radius:10px;border:none;background:#0088cc;color:#fff;'>Back</button>
    </body></html>\"\"\"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    logger.info(f"👤 User {user_id} triggered /start")
    args = message.text.split()
    referrer = args[1] if len(args) > 1 else None
    
    is_new = wallet_logic.register_user(user_id, referrer)
    if is_new:
        logger.info(f"🎉 New user registered: {user_id} (Referrer: {referrer})")
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("💰 Open Wallet", web_app=telebot.types.WebAppInfo(f"{WEBHOOK_URL}/gui/wallet?user_id={user_id}")))
    bot.send_message(message.chat.id, "Welcome to SLH OS!", reply_markup=markup)

@app.post("/")
async def process_webhook(request: Request):
    json_data = await request.json()
    logger.info(f"📩 Webhook received: {json_data.get('update_id')}")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
