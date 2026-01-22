# -*- coding: utf-8 -*-
import telebot, uvicorn, os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup.add(KeyboardButton("💎 SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("📊 פורטפוליו", "🎁 בונוס יומי")
    bot.send_message(message.chat.id, "💎 **DIAMOND SYSTEM ONLINE**\nהמערכת אותחלה בהצלחה.", reply_markup=markup, parse_mode="HTML")

@app.get("/hub", response_class=HTMLResponse)
async def serve_hub():
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

@app.on_event("startup")
def on_startup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
