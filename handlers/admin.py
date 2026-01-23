import requests
from telebot import types
from utils.config import ADMIN_ID

def get_ton_gas_price():
    try:
        res = requests.get("https://toncenter.com/api/v2/getConsensusBlock", timeout=5).json()
        return "Online (Standard Fees)"
    except:
        return "Network Busy"

def register_admin_handlers(bot):
    @bot.message_handler(commands=['admin'])
    def admin_dashboard(message):
        if str(message.from_user.id) == ADMIN_ID:
            gas_status = get_ton_gas_price()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📥 בקשות רכישה ממתינות", callback_data="view_pending"))
            
            bot.send_message(
                message.chat.id,
                f"📊 **מערכת ניהול - SLH OS**\n\n" +
                f"⛽ סטטוס גז ב-TON: {gas_status}\n" +
                f"🛠 גרסת אדמין: 2.0",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            bot.reply_to(message, "❌ אין לך הרשאות ניהול.")
