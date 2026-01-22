import telebot, uvicorn, psycopg2
from fastapi import FastAPI, Request
from utils.config import (
    TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID, TOKEN_PACKS, 
    WIN_CHANCE, BOT_USERNAME, DATABASE_URL
)
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight
from handlers.saas import get_support_info, get_marketplace
from handlers.marketing import process_referral

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db():
    return psycopg2.connect(DATABASE_URL)

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💳 פורטפוליו & ארנק", "🤖 סוכן AI אסטרטגי", "🕹️ ארקייד Supreme", "🛒 חנות הבוטים", "🎁 הזמן חברים", "📞 תמיכה וקשר")
    return markup

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM ONLINE**", reply_markup=main_menu())

# --- פקודת אדמין להוספת טוקנים (החלום!) ---
@bot.message_handler(commands=['add_cash'])
def add_cash(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    try:
        args = message.text.split()
        target_id = args[1]
        amount = int(args[2])
        
        conn = get_db(); cur = conn.cursor()
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, target_id))
        conn.commit(); cur.close(); conn.close()
        
        bot.reply_to(message, f"✅ הופקדו {amount} SLH לחשבון {target_id} בהצלחה!")
        bot.send_message(target_id, f"🎁 **מתנה מהנהלת המערכת!**\nהופקדו בחשבונך {amount} SLH.")
    except Exception as e:
        bot.reply_to(message, "❌ שימוש: /add_cash [ID] [כמות]")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text
    chat_id = message.chat.id
    user_id = str(message.from_user.id)

    if text == "💳 פורטפוליו & ארנק":
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance, xp, rank FROM users WHERE user_id = %s", (user_id,))
        u = cur.fetchone()
        if not u:
            cur.execute("INSERT INTO users (user_id) VALUES (%s) RETURNING balance, xp, rank", (user_id,))
            u = cur.fetchone()
            conn.commit()
        cur.close(); conn.close()
        bot.send_message(chat_id, f"👤 **פרופיל משקיע**\n💰 יתרה: {u[0]} SLH\n🏅 דרגה: {u[2]}")

    elif text == "🤖 סוכן AI אסטרטגי":
        bot.send_message(chat_id, get_market_insight(user_id))

    elif text == "🛒 חנות הבוטים":
        bot.send_message(chat_id, f"{get_marketplace()}\n\n💎 **חבילות:**\n{TOKEN_PACKS}")

    elif text == "🕹️ ארקייד Supreme":
        bot.send_message(chat_id, f"🎰 **סיכויי זכייה:** {WIN_CHANCE}%\nהימור על קוביה (6) ב-50 SLH:", 
                         reply_markup=telebot.types.InlineKeyboardMarkup().add(
                             telebot.types.InlineKeyboardButton("🎲 שחק עכשיו", callback_data="play_50")))

    elif text == "🎁 הזמן חברים":
        bot.send_message(chat_id, f"🔗 לינק השותפים שלך:\nhttps://t.me/{BOT_USERNAME}?start={user_id}")

    elif text == "📞 תמיכה וקשר":
        bot.send_message(chat_id, get_support_info(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "play_50")
def callback_play(call):
    res = play_dice(call.message.chat.id, str(call.from_user.id), 50, 6)
    bot.send_message(call.message.chat.id, res)

@app.on_event("startup")
def on_startup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
