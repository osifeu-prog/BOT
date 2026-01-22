# -*- coding: utf-8 -*-
import telebot, os, psycopg2
from utils.config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

def get_db(): return psycopg2.connect(DATABASE_URL)

# --- פקודת העברת SLH בין חברים (כלכלה חופשית) ---
@bot.message_handler(commands=['send'])
def send_coins(message):
    try:
        # פורמט: /send [ID] [כמות]
        args = message.text.split()
        recipient_id = args[1]
        amount = int(args[2])
        sender_id = str(message.from_user.id)
        
        if amount <= 0: raise ValueError()

        conn = get_db(); cur = conn.cursor()
        # בדיקת יתרה
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (sender_id,))
        balance = cur.fetchone()[0]
        
        if balance < amount:
            bot.reply_to(message, "❌ יתרה נמוכה מדי לביצוע ההעברה.")
        else:
            # ביצוע ההעברה בתוך ה-Ledger
            cur.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, sender_id))
            cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, recipient_id))
            # תיעוד התנועה (הזרע של ה-Blockchain)
            cur.execute("INSERT INTO transactions (from_id, to_id, amount) VALUES (%s, %s, %s)", (sender_id, recipient_id, amount))
            conn.commit()
            bot.reply_to(message, f"✅ העברת {amount} SLH למשתמש {recipient_id} בוצעה בהצלחה!")
            bot.send_message(recipient_id, f"💰 קיבלת {amount} SLH מהמשתמש {sender_id}!")
        
        cur.close(); conn.close()
    except:
        bot.reply_to(message, "📝 שימוש: /send [מזהה_משתמש] [כמות]")

# --- הצגת נתוני מאקרו של הכלכלה ---
@bot.message_handler(commands=['economy'])
def economy_stats(message):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(balance) FROM users")
    users_count, total_supply = cur.fetchone()
    cur.close(); conn.close()
    
    msg = (
        f"📊 **מצב הכלכלה של SLH**\n\n"
        f"👥 מספר ריבונים בקהילה: {users_count}\n"
        f"💰 סך מטבעות בסירקולציה: {total_supply}\n"
        f"🏢 נדל"ן רשום: בקרוב..."
    )
    bot.reply_to(message, msg, parse_mode="HTML")

