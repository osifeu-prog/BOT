# -*- coding: utf-8 -*-
import telebot, uvicorn, psycopg2, os, random
from fastapi import FastAPI, Request
from telebot.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from utils.config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

# הגדרת תפריט פקודות רשמי בטלגרם
def set_commands():
    commands = [
        BotCommand("start", "🚀 התחלת הבוט"),
        BotCommand("profile", "👤 הפרופיל שלי"),
        BotCommand("ai", "🤖 עוזר AI"),
        BotCommand("admin", "👑 ניהול (אדמין בלבד)")
    ]
    bot.set_my_commands(commands)

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
    conn.commit(); cur.close(); conn.close()
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    hub_url = f"{WEBHOOK_URL.split('/8106')[0]}/hub"
    markup.add(KeyboardButton("💎 SUPREME HUB", web_app=WebAppInfo(url=hub_url)))
    markup.add("📊 פורטפוליו", "👤 פרופיל", "🎁 בונוס יומי", "🤖 AI עוזר")
    
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME ONLINE**\nהמערכת מחוברת ומוכנה לעבודה.", reply_markup=markup, parse_mode="HTML")

# --- מנגנון שידור (Broadcast) לאדמין ---

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def ask_broadcast_msg(call):
    msg = bot.send_message(call.message.chat.id, "📝 שלח לי עכשיו את ההודעה שתרצה להפיץ לכל המשתמשים:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    if str(message.from_user.id) != ADMIN_ID: return
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    cur.close(); conn.close()
    
    count = 0
    for user in users:
        try:
            bot.send_message(user[0], f"📢 **הודעת מערכת:**\n\n{message.text}", parse_mode="HTML")
            count += 1
        except: pass
    
    bot.send_message(ADMIN_ID, f"✅ השידור הסתיים! ההודעה נשלחה ל-{count} משתמשים.")

# --- API ושאר הפונקציות ---

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) != ADMIN_ID: return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 שידור הודעה לכולם", callback_data="broadcast"))
    bot.send_message(message.chat.id, f"👑 **פאנל ניהול אדמין**\nסיכוי זכייה: {WIN_CHANCE*100}%\nפרס הזמנה: {REFERRAL_REWARD}", reply_markup=markup)

@app.post(f"/{TELEGRAM_TOKEN}/")
async def web(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

@app.on_event("startup")
def setup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
    set_commands() # מעדכן את התפריט בטלגרם
