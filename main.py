# -*- coding: utf-8 -*-
import telebot, os
from utils.config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# פונקציה לקריאת קבצי הפרוטוקול מהתיקייה
def read_doc(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "❌ הקובץ לא נמצא בשרת."

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) != ADMIN_ID: return
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📜 הצג חזון (VISION)", callback_data="view_vision"))
    markup.add(telebot.types.InlineKeyboardButton("🛠️ מפרט טכני (TECH)", callback_data="view_tech"))
    markup.add(telebot.types.InlineKeyboardButton("📢 שידור עדכון פרוטוקול", callback_data="broadcast"))
    
    bot.send_message(message.chat.id, "👑 **ניהול פרוטוקול SLH**\nבחר קובץ לצפייה או עדכון:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_"))
def handle_docs(call):
    doc_map = {
        "view_vision": "SLH_VISION.md",
        "view_tech": "SLH_TECH.md"
    }
    filename = doc_map.get(call.data)
    content = read_doc(filename)
    # שולח את התוכן של הקובץ כהודעה
    bot.send_message(call.message.chat.id, f"📝 **תוכן הקובץ {filename}:**\n\n{content[:4000]}")

# פקודה ציבורית לכולם
@bot.message_handler(commands=['docs'])
def public_docs(message):
    bot.reply_to(message, "📚 מסמכי הפרוטוקול זמינים בגיטהאב או דרך פקודת /manifesto")

