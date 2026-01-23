# -*- coding: utf-8 -*-
import logging
import os
import sys
import telebot
from fastapi import FastAPI, Request
from telebot import types
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
from handlers import wallet_logic, saas, router, admin, ai_agent
import uvicorn

# הגדרת לוגים מתקדמת
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SLH_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"User {message.from_user.id} started the bot")
    
    # כפתור המיני-סייט (Web App)
    markup = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(f"{WEBHOOK_URL}/gui/wallet?user_id={message.from_user.id}")
    btn_site = types.InlineKeyboardButton("🌐 פתח ארנק (Mini-App)", web_app=web_app)
    btn_gift = types.InlineKeyboardButton("🎁 צור מתנה", callback_data="create_gift")
    markup.add(btn_site)
    markup.add(btn_gift)
    
    welcome_text = (
        "💎 **SLH OS v2.0 - Active**\n"
        "ברוך הבא למערכת הניהול הריבונית.\n\n"
        "הארנק שלך מסונכרן כעת כמיני-סייט."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# חיבור שאר הפקודות (שחזור)
@bot.message_handler(commands=['ai'])
def ai_cmd(message): ai_agent.handle_ai(bot, message)

@bot.message_handler(commands=['admin'])
def admin_cmd(message): admin.handle_admin(bot, message)

@app.post("/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

@app.get("/gui/wallet")
def wallet_gui(user_id: str):
    # כאן יוגש ה-HTML של המיני-סייט (בעתיד נוכל לשים קובץ HTML נפרד)
    return {"message": "Wallet Mini-Site is under construction", "user_id": user_id}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}...")
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    uvicorn.run(app, host="0.0.0.0", port=port)
