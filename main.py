# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, os, random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- פקודות בוט מלאות ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    # יצירת משתמש אם לא קיים
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup.add(KeyboardButton("💎 SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("📊 פורטפוליו", "👤 פרופיל", "🎁 בונוס יומי", "🤖 AI עוזר")
    bot.send_message(message.chat.id, f"💎 **ברוך הבא ל-DIAMOND SUPREME**\n\nכאן תוכל לסחור, לשחק ולהרוויח.", reply_markup=markup, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👤 פרופיל" or m.text == "/profile")
def profile(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
    res = cur.fetchone()
    balance = res[0] if res else 0
    cur.close(); conn.close()
    bot.reply_to(message, f"👤 **הפרופיל שלך:**\n\n🆔 מזהה: {uid}\n💰 יתרה: {balance} SLH", parse_mode="HTML")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) == ADMIN_ID:
        bot.reply_to(message, "👑 **פאנל ניהול אדמין**\n\nהגדרות נוכחיות:\nסיכוי זכייה: " + str(WIN_CHANCE*100) + "%\nפרס הזמנה: " + str(REFERRAL_REWARD))
    else:
        bot.reply_to(message, "❌ אין לך הרשאות ניהול.")

@bot.message_handler(commands=['ai'])
def ai_assistant(message):
    bot.reply_to(message, "🤖 עוזר ה-AI בודק את השוק עבורך... (מתחבר ל-OpenAI)")

# --- API לממשק ה-WEB (HUB) ---

@app.get("/api/user_data/{uid}")
async def user_data(uid: str):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (uid,))
    res = cur.fetchone()
    cur.close(); conn.close()
    return {"balance": res[0] if res else 1000}

@app.get("/hub", response_class=HTMLResponse)
async def serve_hub():
    with open("hub.html", "r", encoding="utf-8") as f: return f.read()

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

@app.on_event("startup")
def setup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
