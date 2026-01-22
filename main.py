# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, logging, os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

# פתרון לבעיית הג'יבריש - הגדרת קידוד גלובלי
logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
ADMIN_ID = "224223270"

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- ממשק SUPREME HUB מאוחד ---
@app.get("/hub", response_class=HTMLResponse)
async def get_hub():
    # קובץ אחד שמרכז גם ארנק וגם משחקים בטאבים
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

def main_menu(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    # לינק אחד ויחיד לכל המערכת הגרפית
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup.add(KeyboardButton("💎 SUPREME HUB (Wallet & Games)", web_app=WebAppInfo(url=hub_url)))
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים", "👥 הזמן חברים", "🎁 בונוס יומי")
    if str(uid) == ADMIN_ID: markup.add("👑 פאנל ניהול")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    # וידוא רישום ב-DB
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    welcome_text = "💎 **DIAMOND SUPREME SYSTEM**\nברוך הבא לממשק היוקרה המאוחד."
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(uid), parse_mode="HTML")

# --- שאר הפקודות (פורטפוליו, אדמין וכו') נשארות כפי שהן אך עם תיקון טקסט ---
@app.post(f"/{TELEGRAM_TOKEN}/")
async def process(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup(): bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
