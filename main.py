# -*- coding: utf-8 -*-
import telebot
from fastapi import FastAPI, Request
from utils.config import *
from utils.protocol import protocol
from texts.messages import *

app = FastAPI()
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🏗️ סטטוס מערכת", callback_data="sys_status"))
    markup.add(telebot.types.InlineKeyboardButton("📚 איך לתעד?", callback_data="view_docs"))
    bot.reply_to(message, WELCOME_MSG, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "sys_status":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, SYSTEM_INFO, parse_mode="HTML")
    elif call.data == "view_docs":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🛒 לרכישת התיעוד המלא", url=protocol.docs_link))
        bot.send_message(call.message.chat.id, DOCS_GUIDE, reply_markup=markup, parse_mode="HTML")

bot.remove_webhook()
bot.set_webhook(url=f"https://bot-production-2668.up.railway.app/{TELEGRAM_TOKEN}/")
