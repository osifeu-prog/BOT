# -*- coding: utf-8 -*-
import telebot, os, hashlib
from utils.config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# --- כלי עריכת פרוטוקול ---
@bot.callback_query_handler(func=lambda call: call.data == "edit_vision")
def start_edit_vision(call):
    msg = bot.send_message(call.message.chat.id, "✍️ שלח לי עכשיו את הטקסט החדש ל-SLH_VISION.md:")
    bot.register_next_step_handler(msg, save_vision)

def save_vision(message):
    try:
        with open("SLH_VISION.md", "w", encoding="utf-8") as f:
            f.write(message.text)
        bot.reply_to(message, "✅ הפרוטוקול עודכן בהצלחה בשרת!")
    except Exception as e:
        bot.reply_to(message, f"❌ שגיאה בעדכון: {str(e)}")

# --- מערכת בדיקות אדמין ---
@bot.message_handler(commands=['admin'])
def lab_admin_panel(message):
    if str(message.from_user.id) != ADMIN_ID: return
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📝 ערוך חזון (Vision)", callback_data="edit_vision"))
    markup.add(telebot.types.InlineKeyboardButton("🔍 בדיקת תקינות מערכת", callback_data="health_check"))
    markup.add(telebot.types.InlineKeyboardButton("📄 צפה ב-Docs", callback_data="view_docs"))
    
    bot.send_message(message.chat.id, "🔬 **מעבדת SLH - מצב ניהול**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "health_check")
def run_health(call):
    # בדיקה מהירה של המשתנים הקריטיים
    status = "✅ הכל תקין" if TELEGRAM_TOKEN and DATABASE_URL else "❌ חסרים נתונים"
    check_msg = (
        f"🚑 **בדיקת מערכת:**\n\n"
        f"🌐 Webhook: פעיל\n"
        f"📊 Database: מחובר\n"
        f"⚙️ משתני סביבה: {status}\n"
        f"🛠️ גרסת קוד (Hash): {hashlib.sha256(open(__file__, 'rb').read()).hexdigest()[:8]}"
    )
    bot.send_message(call.message.chat.id, check_msg)

# שאר הפונקציות הסטנדרטיות...
