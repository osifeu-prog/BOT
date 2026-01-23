# -*- coding: utf-8 -*-
import logging
import sys
import os
import telebot
from fastapi import FastAPI, Request
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
from handlers import wallet_logic, saas, router, admin
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.post("/")
async def process_webhook(request: Request):
    try:
        json_data = await request.json()
        update = telebot.types.Update.de_json(json_data)
        # שים לב לשורה הזו - היא הקריטית!
        bot.process_new_updates([update])
        logger.info(f"✅ Processed update from user")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return {"status": "error"}

@app.get("/")
def health_check():
    return {"status": "Online"}

# ה-Handlers שלך
@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"🚀 Received /start from {message.from_user.id}")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_wallet = telebot.types.InlineKeyboardButton('💰 הארנק שלי', callback_data='view_wallet')
    btn_estate = telebot.types.InlineKeyboardButton('🏠 נדל"ן וריבונות', callback_data='real_estate')
    markup.add(btn_wallet, btn_estate)
    bot.reply_to(message, "💎 **SLH OS Core - Webhook Active**\nהמערכת מוכנה לפעולה.", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == 'view_wallet':
        bot.send_message(call.message.chat.id, wallet_logic.show_wallet(call.from_user.id))
    elif call.data == 'real_estate':
        bot.send_message(call.message.chat.id, saas.get_support_info(), parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
