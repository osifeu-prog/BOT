from telebot import types
from utils.config import ADMIN_ID

def register_wallet_handlers(bot):
    @bot.message_handler(commands=['buy'])
    def buy_request(message):
        msg = bot.send_message(message.chat.id, "💰 כמה מטבעות SLH תרצה לרכוש? (1 ש\"ח = 1 מטבע)")
        bot.register_next_step_handler(msg, lambda m: send_to_admin(m, bot))

    def send_to_admin(message, bot):
        try:
            amount = int(message.text)
            user_id = message.from_user.id
            username = message.from_user.username or "Unknown"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ אישרתי תשלום", callback_data=f"pay_ok_{user_id}_{amount}"))
            
            bot.send_message(
                ADMIN_ID,
                f"🔔 **בקשת רכישה חדשה!**\n\n" +
                f"משתמש: @{username}\n" +
                f"כמות: {amount} SLH\n" +
                f"לתשלום: {amount} ש\"ח\n\n" +
                "לאחר קבלת התשלום, לחץ על האישור לשליחת המטבעות מה-Railway.",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            bot.send_message(message.chat.id, "✅ בקשתך נשלחה לאדמין לאישור.")
        except:
            bot.send_message(message.chat.id, "❌ נא להזין מספר שלם בלבד.")
