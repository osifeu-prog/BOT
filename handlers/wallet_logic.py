from telebot import types
from utils.config import ADMIN_ID
from db.connection import get_conn
import logging

logger = logging.getLogger("SLH_OS")

def get_user_full_data(user_id):
    """מושך נתונים למיני-אפ"""
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT balance, xp, rank FROM users WHERE user_id = %s", (str(user_id),))
        res = cur.fetchone()
        cur.close()
        if res:
            return res[0], res[1], res[2]
        return 0, 0, "Starter"
    except Exception as e:
        logger.error(f"Error in get_user_full_data: {e}")
        return 0, 0, "Error"
    finally:
        if conn: conn.close()

def register_user(user_id):
    """רישום משתמש חדש"""
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (user_id, balance, xp, rank) VALUES (%s, 0, 0, 'Starter') ON CONFLICT DO NOTHING", (str(user_id),))
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Error registering user: {e}")
    finally:
        if conn: conn.close()

def register_wallet_handlers(bot):
    @bot.message_handler(commands=['buy'])
    def buy_request(message):
        msg = bot.send_message(message.chat.id, "💰 כמה מטבעות SLH תרצה לרכוש? (1 ש\"ח = 1 מטבע)")
        bot.register_next_step_handler(msg, lambda m: send_to_admin(m, bot))

    def send_to_admin(message, bot):
        try:
            amount = int(message.text)
            user_id = message.from_user.id
            username = message.from_user.username or "User"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ אישרתי תשלום", callback_data=f"pay_ok_{user_id}_{amount}"))
            bot.send_message(ADMIN_ID, f"🔔 **בקשה חדשה!**\n\nמשתמש: @{username}\nID: {user_id}\nכמות: {amount} SLH", reply_markup=markup, parse_mode="Markdown")
            bot.send_message(message.chat.id, "✅ בקשתך נשלחה לאדמין לאישור.")
        except:
            bot.send_message(message.chat.id, "❌ נא להזין מספר שלם.")
