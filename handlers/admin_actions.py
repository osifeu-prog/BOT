from telebot import types
from handlers import wallet_logic
from utils.config import ADMIN_ID

def register_admin_actions(bot):
    @bot.message_handler(commands=['gift'])
    def gift_tokens(message):
        if str(message.from_user.id) != str(ADMIN_ID):
            return
        
        try:
            args = message.text.split()
            target_id = args[1]
            amount = float(args[2])
            
            # ביצוע ההעברה ב-DB
            if wallet_logic.add_balance(target_id, amount):
                bot.reply_to(message, f"🎁 שלחת {amount} SLH למשתמש {target_id}!")
                bot.send_message(target_id, f"🎉 קיבלת מתנה מהמנהל: {amount} SLH!")
            else:
                bot.reply_to(message, "❌ שגיאה בהעברה. וודא שהמשתמש רשום.")
        except:
            bot.reply_to(message, "⚠️ שימוש: /gift [USER_ID] [AMOUNT]")
