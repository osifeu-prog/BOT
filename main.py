# -*- coding: utf-8 -*-
import telebot
import os
from utils.config import TELEGRAM_TOKEN
# ייבוא המודולים הקיימים שלך
from handlers import admin, ai_agent, arcade, callback_router, marketing, router, saas, wallet_logic

# אתחול הבוט במצב פשוט
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    # שים לב: השתמשתי בגרש בודד כדי לא לשבור את הקוד עם המילה נדל"ן
    markup.add(telebot.types.InlineKeyboardButton('🏠 נדל"ן וריבונות', callback_data='real_estate'))
    markup.add(telebot.types.InlineKeyboardButton('💰 ארנק דיגיטלי', callback_data='wallet_main'))
    bot.reply_to(message, "💎 SLH OS Core\nהמערכת שוחזרה בהצלחה.", reply_markup=markup)

if __name__ == "__main__":
    print("--- המערכת עלתה בהצלחה במחשב המקומי ---")
    bot.remove_webhook()
    bot.polling(none_stop=True)
