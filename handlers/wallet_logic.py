from telebot import types
from utils.config import ADMIN_ID
import db.connection as db_conn

def register_user(user_id):
    """רישום משתמש בצורה בטוחה שתואמת לכל מבנה DB"""
    try:
        # אנחנו משתמשים בגישה גנרית כדי לא לשבור את החיבור
        with db_conn.conn.cursor() as cur:
            cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 0) ON CONFLICT DO NOTHING", (user_id,))
            db_conn.conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")

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
                "אשר לאחר קבלת התשלום.",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            bot.send_message(message.chat.id, "✅ בקשתך נשלחה לאדמין לאישור.")
        except Exception:
            bot.send_message(message.chat.id, "❌ נא להזין מספר שלם בלבד.")
