# -*- coding: utf-8 -*-
import telebot
from fastapi import FastAPI, Request
from utils.config import *
from utils.protocol import protocol

app = FastAPI()
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# הגדרת נתיב ה-Webhook הדינמי של טלגרם
@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    json_string = await request.json()
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"status": "ok"}

@app.get("/")
def health_check():
    return {"status": "online", "version": protocol.version, "system": protocol.system_name}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "💎 **SLH OS - Active**\nהמערכת מסונכרנת ומחכה לפקודות.")

@bot.message_handler(commands=['system'])
def system(message):
    bot.reply_to(message, f"🏗️ **סטטוס מערכת**\nגרסה: {protocol.version}\nשכבות: Core, Ledger, Vault")

# הסרת Webhook ישן והגדרה מחדש בטעינה
bot.remove_webhook()
bot.set_webhook(url=f"https://bot-production-2668.up.railway.app/{TELEGRAM_TOKEN}/")
