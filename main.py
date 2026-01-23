# -*- coding: utf-8 -*-
import logging, os, telebot, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telebot import types
from utils.config import * # טוען את כל המשתנים מ-config
from handlers import wallet_logic
from db.connection import init_db

# הגדרת לוגים משופרת ל-Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("SLH_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# פקודת התקנה/איפוס
@bot.message_handler(commands=['install'])
def install_cmd(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        logger.info(f"Admin {message.from_user.id} triggered /install")
        init_db()
        bot.reply_to(message, "⚙️ **התקנה הושלמה:** בסיס הנתונים עודכן והעמודות סונכרנו.")

# פקודת שליחת מטבעות ידנית (למשל לבדיקה בטסט-נט)
@bot.message_handler(commands=['send'])
def send_coins(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        try:
            _, target_id, amount = message.text.split()
            success, msg = wallet_logic.manual_transfer(target_id, float(amount))
            bot.reply_to(message, f"💸 **סטטוס העברה:** {msg}")
            logger.info(f"Manual Transfer: {amount} SLH to {target_id}")
        except:
            bot.reply_to(message, "❌ פורמט: /send [USER_ID] [AMOUNT]")

# פקודת סטטיסטיקות עומק
@bot.message_handler(commands=['stats'])
def full_stats(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        # משיכת נתונים מהלוגיקה
        stats = wallet_logic.get_system_stats()
        text = (
            f"📊 **דו''ח מערכת SLH:**\n\n"
            f"👥 משתמשים: {stats['users']}\n"
            f"💰 סה''כ SLH במחזור: {stats['total_supply']}\n"
            f"🔄 עסקאות: {stats['tx_count']}\n"
            f"🔗 שרת: Railway Active"
        )
        bot.reply_to(message, text)

@bot.message_handler(commands=['start'])
def handle_start(message):
    # שימוש במשתנה REFERRAL_REWARD מ-Railway
    ref_reward = os.environ.get('REFERRAL_REWARD', '2') 
    wallet_logic.register_user(message.from_user.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    url = f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}"
    markup.add(types.KeyboardButton("🏦 פתח ארנק Web3", web_app=types.WebAppInfo(url)))
    
    bot.send_message(
        message.chat.id, 
        f"💎 **ברוך הבא ל-SLH OS**\nהזמן חברים וקבל {ref_reward} SLH בונוס!",
        reply_markup=markup
    )

@app.get("/gui/wallet", response_class=HTMLResponse)
def wallet_gui(user_id: str):
    # הקוד של ה-UI נשאר כפי שהיה
    balance, xp, rank, addr = wallet_logic.get_user_full_data(user_id)
    txs = wallet_logic.get_last_transactions(user_id)
    # ... (המשך ה-HTML מהגרסה הקודמת)
    return "UI Code Here" # לצורך הקיצור, נשמור את ה-HTML הקודם שלך

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

if __name__ == "__main__":
    init_db() # הרצה אוטומטית בעליית השרת
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
