from telebot import types
from utils.config import ADMIN_ID
from db.connection import get_conn
import logging

logger = logging.getLogger("SLH_OS")

def get_user_full_data(user_id):
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
        logger.error(f"Error: {e}")
        return 0, 0, "Error"
    finally:
        if conn: conn.close()

def get_economy_stats():
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT SUM(balance), COUNT(*) FROM users")
        res = cur.fetchone()
        cur.close()
        return (res[0] if res[0] else 0), (res[1] if res[1] else 0)
    except:
        return 0, 0
    finally:
        if conn: conn.close()

def register_wallet_handlers(bot):
    @bot.message_handler(commands=['send'])
    def send_coins(message):
        bot.send_message(message.chat.id, "💸 Usage: /send ID AMOUNT")

    @bot.message_handler(commands=['buy'])
    def buy_coins(message):
        bot.send_message(message.chat.id, "💰 Contact admin to buy SLH coins.")
