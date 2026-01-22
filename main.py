# -*- coding: utf-8 -*-
import telebot
from fastapi import FastAPI
from utils.config import *
from utils.protocol import protocol

# זה ה-Attribute ש-Railway חיפש!
app = FastAPI()
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

@app.get("/")
def health_check():
    return {"status": "online", "version": protocol.version}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "💎 **SLH OS - Online**\nהמערכת מוכנה ומאובטחת.")

@bot.message_handler(commands=['system'])
def system(message):
    bot.reply_to(message, f"🏗️ **מבנה המערכת**\nגרסה: {protocol.version}\nסטטוס: פעיל")

# נקודת הקצה עבור Webhooks (אם תרצה בעתיד)
@app.post("/")
def process_webhook(update: dict):
    if update:
        telebot.types.Update.de_json(update)
    return "OK"

# הרצה פשוטה עבור פייתון
if __name__ == "__main__":
    bot.polling(none_stop=True)
