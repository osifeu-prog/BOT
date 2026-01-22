import telebot, os, psycopg2
from utils.config import TELEGRAM_TOKEN, ADMIN_ID, DATABASE_URL
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight
from handlers.saas import get_support_info, get_marketplace
from handlers.marketing import generate_affiliate_link, process_referral

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_db():
    return psycopg2.connect(DATABASE_URL)

# --- תפריטים (Keyboards) ---
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💳 הפורטפוליו שלי", "🤖 סוכן AI אישי", "🕹️ ארקייד Supreme", "🎁 בונוס יומי", "🛒 חנות הבוטים", "📞 תמיכה וקשר")
    return markup

def arcade_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 הימור: 50 SLH", "💰 הימור: 100 SLH", "🔙 חזרה לתפריט")
    return markup

# --- ניהול פקודות ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    referrer_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", (user_id,))
    conn.commit(); cur.close(); conn.close()
    
    if referrer_id:
        process_referral(user_id, referrer_id)
    
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME SYSTEM**\nברוך הבא לאימפריה הפיננסית שלך.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    text = message.text

    if text == "💳 הפורטפוליו שלי":
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT balance, xp, rank FROM users WHERE user_id = %s", (user_id,))
        u = cur.fetchone()
        cur.close(); conn.close()
        bot.send_message(chat_id, f"👤 **פרופיל משקיע**\n\n💰 יתרה: {u[0]} SLH\n🏆 XP: {u[1]}\n🏅 דרגה: {u[2]}")

    elif text == "🤖 סוכן AI אישי":
        bot.send_message(chat_id, get_market_insight(user_id), parse_mode="Markdown")

    elif text == "🕹️ ארקייד Supreme":
        bot.send_message(chat_id, "🎰 בחר סכום הימור:", reply_markup=arcade_menu())

    elif text.startswith("💰 הימור:"):
        amt = text.split(":")[1].split()[0]
        markup = telebot.types.InlineKeyboardMarkup()
        btns = [telebot.types.InlineKeyboardButton(f"🎲 {i}", callback_data=f"dice_{amt}_{i}") for i in range(1, 7)]
        markup.add(*btns)
        bot.send_message(chat_id, f"נחש מספר (הימור {amt} SLH):", reply_markup=markup)

    elif text == "🛒 חנות הבוטים":
        bot.send_message(chat_id, get_marketplace())

    elif text == "📞 תמיכה וקשר":
        bot.send_message(chat_id, get_support_info(), parse_mode="Markdown", disable_web_page_preview=True)

    elif text == "🔙 חזרה לתפריט":
        bot.send_message(chat_id, "חוזר לתפריט הראשי...", reply_markup=main_menu())

    else:
        # רישום ליומן (Market Journal)
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO journal (user_id, entry) VALUES (%s, %s)", (user_id, text))
        conn.commit(); cur.close(); conn.close()
        bot.send_message(chat_id, "📝 נרשם ביומן השוק. הסוכן מעבד את המידע.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("dice_"))
def callback_dice(call):
    _, amt, guess = call.data.split("_")
    res = play_dice(call.message.chat.id, str(call.from_user.id), int(amt), guess)
    bot.send_message(call.message.chat.id, res)

if __name__ == "__main__":
    print("🚀 Empire Online - System Live")
    bot.polling(none_stop=True)
