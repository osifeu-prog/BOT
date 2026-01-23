# -*- coding: utf-8 -*-
import telebot
from utils.config import TELEGRAM_TOKEN
# ייבוא המודולים שהסריקה הראתה שקיימים
from handlers import wallet_logic, saas, router, admin

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# --- פקודות ליבה שמשלבות את המודולים שלך ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    # כאן אנחנו משתמשים בלוגיקה מתוך ה-wallet_logic שסרקנו
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_wallet = telebot.types.InlineKeyboardButton('💰 הארנק שלי', callback_data='view_wallet')
    btn_estate = telebot.types.InlineKeyboardButton('🏠 נדלן וריבונות', callback_data='real_estate')
    markup.add(btn_wallet, btn_estate)
    
    bot.reply_to(message, "💎 **SLH OS Core - המערכת פעילה**\nכל המודולים סונכרנו בהצלחה.", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == 'view_wallet':
        # קריאה לפונקציה מתוך wallet_logic.py
        wallet_text = wallet_logic.show_wallet(call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, wallet_text)
    
    elif call.data == 'real_estate':
        # קריאה לפונקציה מתוך saas.py שסרקנו
        support_info = saas.get_support_info()
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, support_info, parse_mode="Markdown")

if __name__ == "__main__":
    print("--- SLH OS is booting up ---")
    bot.remove_webhook()
    # מצב פולינג מקומי לבדיקה
    bot.polling(none_stop=True)
