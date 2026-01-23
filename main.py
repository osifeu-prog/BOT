# -*- coding: utf-8 -*-
import logging
import sys
import os
import telebot
from fastapi import FastAPI, Request
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
# ייבוא כל ה-Handlers
from handlers import wallet_logic, saas, router, admin, ai_agent, arcade
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

# --- חיבור ה-Handlers של המודולים לבוט הראשי ---
# כאן אנחנו אומרים לבוט להשתמש בפונקציות מהקבצים האחרים
@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    admin.handle_admin(bot, message)

@bot.message_handler(commands=['ai'])
def ai_cmd(message):
    ai_agent.handle_ai(bot, message)

@bot.message_handler(commands=['profile', 'wallet'])
def profile_cmd(message):
    bot.reply_to(message, wallet_logic.show_wallet(message.from_user.id))

@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"🚀 Received /start from {message.from_user.id}")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_wallet = telebot.types.InlineKeyboardButton('💰 הארנק שלי', callback_data='view_wallet')
    btn_estate = telebot.types.InlineKeyboardButton('🏠 נדל"ן וריבונות', callback_data='real_estate')
    markup.add(btn_wallet, btn_estate)
    bot.reply_to(message, "💎 **SLH OS Core - Full Access**\nהמערכת פעילה עם כל המודולים.", parse_mode="HTML", reply_markup=markup)

# טיפול בכפתורים (Callback Queries)
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == 'view_wallet':
        bot.send_message(call.message.chat.id, wallet_logic.show_wallet(call.from_user.id))
    elif call.data == 'real_estate':
        bot.send_message(call.message.chat.id, saas.get_support_info(), parse_mode="Markdown")

@app.post("/")
async def process_webhook(request: Request):
    try:
        json_data = await request.json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Webhook Error: {e}")
        return {"status": "error"}

@app.get("/")
def health_check():
    return {"status": "Active"}

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
