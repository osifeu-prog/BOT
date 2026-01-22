import telebot, uvicorn, psycopg2
from fastapi import FastAPI, Request
from utils.config import (
    TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID, OPENAI_API_KEY, 
    TOKEN_PACKS, WIN_CHANCE, BOT_USERNAME, BASE_URL, 
    SUPPORT_PHONE, SUPPORT_EMAIL, DATABASE_URL
)
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight
from handlers.saas import get_support_info, get_marketplace
from handlers.marketing import process_referral

# אתחול
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db():
    return psycopg2.connect(DATABASE_URL)

# --- תפריטים מרהיבים ---
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💳 פורטפוליו & ארנק", "🤖 סוכן AI אסטרטגי", "🕹️ ארקייד Supreme", "🛒 חנות הבוטים", "🎁 הזמן חברים", "📞 תמיכה וקשר")
    return markup

# --- FastAPI Endpoints ---
@app.get("/")
def home():
    return {"status": "Empire Live", "bot": BOT_USERNAME, "site": BASE_URL}

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

# --- Logic Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", (user_id,))
    conn.commit(); cur.close(); conn.close()
    
    if referrer_id:
        process_referral(user_id, referrer_id)
        
    bot.send_message(message.chat.id, f"💎 **ברוך הבא ל-DIAMOND SUPREME**\n\nהמערכת מחוברת ל-PostgreSQL ו-Redis.\nה-WIN CHANCE מוגדר על: {WIN_CHANCE}%", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    text = message.text

    if text == "💳 פורטפוליו & ארנק":
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance, xp, rank FROM users WHERE user_id = %s", (user_id,))
        u = cur.fetchone()
        cur.close(); conn.close()
        bot.send_message(chat_id, f"💰 **מצב חשבון**\n\nיתרה: {u[0]} SLH\nניסיון: {u[1]} XP\nדרגה: {u[2]}")

    elif text == "🛒 חנות הבוטים":
        msg = f"{get_marketplace()}\n\n💎 **חבילות טוקנים זמינות:**\n{TOKEN_PACKS}"
        bot.send_message(chat_id, msg)

    elif text == "🤖 סוכן AI אסטרטגי":
        bot.send_message(chat_id, "🤖 הסוכן סורק את הנתונים שלך...")
        bot.send_message(chat_id, get_market_insight(user_id))

    elif text == "🕹️ ארקייד Supreme":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎲 הימור 50 SLH", callback_data="play_50"))
        bot.send_message(chat_id, "בחר משחק בסיכון גבוה:", reply_markup=markup)

    elif text == "🎁 הזמן חברים":
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        bot.send_message(chat_id, f"🔗 **לינק השותפים שלך:**\n{link}\n\nשתף והרוויח עמלות מכל הפקדה!")

    elif text == "📞 תמיכה וקשר":
        bot.send_message(chat_id, get_support_info(), parse_mode="Markdown")

    else:
        # שמירה ליומן עבור ה-AI
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO journal (user_id, entry) VALUES (%s, %s)", (user_id, text))
        conn.commit(); cur.close(); conn.close()
        bot.send_message(chat_id, "✅ המידע נשמר ביומן ונותח ע\"י ה-AI.")

@bot.callback_query_handler(func=lambda call: call.data == "play_50")
def callback_play(call):
    res = play_dice(call.message.chat.id, str(call.from_user.id), 50, 6) # דוגמה להימור על 6
    bot.send_message(call.message.chat.id, res)

@app.on_event("startup")
def on_startup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")
    print("✅ Webhook Active & Variables Synced")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
