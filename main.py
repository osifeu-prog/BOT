try:
    import psycopg2_binary
    import sys
    sys.modules['psycopg2'] = psycopg2_binary
except ImportError:
    pass
# -*- coding: utf-8 -*-
import telebot
from fastapi import FastAPI, Request
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
from handlers import wallet_logic, saas, router, admin
import uvicorn

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.post("/")
async def process_webhook(request: Request):
    if request.headers.get('content-type') == 'application/json':
        json_string = await request.body()
        update = telebot.types.Update.de_json(json_string.decode('utf-8'))
        bot.process_new_updates([update])
        return {"status": "ok"}
    return {"status": "error"}

@app.get("/")
def health_check():
    return {"status": "SLH OS Core is Online", "webhook": WEBHOOK_URL}

# --- ×—×™×‘×•×¨ ×¤×§×•×“×•×ھ ×‘×،×™×،×™×•×ھ (×›×‍×• ×‍×§×•×“×‌) ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_wallet = telebot.types.InlineKeyboardButton('ًں’° ×”×گ×¨× ×§ ×©×œ×™', callback_data='view_wallet')
    btn_estate = telebot.types.InlineKeyboardButton('ًںڈ  × ×“×œ"×ں ×•×¨×™×‘×•× ×•×ھ', callback_data='real_estate')
    markup.add(btn_wallet, btn_estate)
    bot.reply_to(message, "ًں’ژ **SLH OS Core - Webhook Active**", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == 'view_wallet':
        bot.send_message(call.message.chat.id, wallet_logic.show_wallet(call.from_user.id))
    elif call.data == 'real_estate':
        bot.send_message(call.message.chat.id, saas.get_support_info(), parse_mode="Markdown")

if __name__ == "__main__":
    import os
    # ×”×’×“×¨×ھ ×”-Webhook ×‘×ک×œ×’×¨×‌
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    # ×”×¨×¦×ھ ×”×©×¨×ھ
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# System Patch Applied: 01/23/2026 12:54:41

