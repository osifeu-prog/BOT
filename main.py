# -*- coding: utf-8 -*-
import telebot
from fastapi import FastAPI, Request
from utils.config import *
from utils.protocol import protocol
from texts.messages import *

# ייבוא כל ה-handlers הקיימים שלך
from handlers import admin, ai_agent, arcade, marketing, router, saas, wallet_logic

app = FastAPI()
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# רישום כל ה-handlers למערכת
# (הנחה שהם בנויים כפונקציות register או כ-handlers שמשתמשים ב-bot הגלובלי)
# כאן אנחנו מחברים את הלוגיקה מכל התיקיות
try:
    from handlers.router import register_handlers
    register_handlers(bot)
except:
    pass

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🏠 נדל"ן וריבונות", callback_data="real_estate"),
        telebot.types.InlineKeyboardButton("🎮 ארקייד", callback_data="arcade"),
        telebot.types.InlineKeyboardButton("💰 ארנק", callback_data="wallet"),
        telebot.types.InlineKeyboardButton("🤖 AI Agent", callback_data="ai_chat")
    )
    bot.reply_to(message, WELCOME_MSG, reply_markup=markup, parse_mode="HTML")

# פקודת מערכת שמושכת נתונים אמיתיים
@bot.message_handler(commands=['system'])
def system_check(message):
    status = protocol.get_system_status()
    msg = f"🏗️ **סטטוס מערכת:** {status['status']}\n"
    msg += f"📦 **גרסה:** {protocol.version}\n"
    msg += "📂 **מודולים פעילים:** Admin, AI, Wallet, RealEstate"
    bot.reply_to(message, msg, parse_mode="HTML")

bot.remove_webhook()
bot.set_webhook(url=f"https://bot-production-2668.up.railway.app/{TELEGRAM_TOKEN}/")
