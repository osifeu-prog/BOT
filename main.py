import telebot, uvicorn, psycopg2, logging, os
from fastapi import FastAPI, Request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from utils.config import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SAAS_CORE")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

def get_db(): return psycopg2.connect(DATABASE_URL)

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    # ×‘×“×™×§×” ×گ×‌ ×”×‍×©×ھ×‍×© ×”×’×™×¢ ×“×¨×ڑ ×œ×™× ×§ ×”×¤× ×™×”
    ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, balance) VALUES (%s, 1000) ON CONFLICT DO NOTHING", (uid,))
        logger.info(f"ًں†• NEW USER JOINED: {uid}")
        if ref_id and ref_id != uid:
            cur.execute("UPDATE users SET balance = balance + 500 WHERE user_id = %s", (ref_id,))
            cur.execute("UPDATE users SET balance = balance + 200 WHERE user_id = %s", (uid,))
            logger.info(f"ًںژپ REFERRAL BONUS: {ref_id} invited {uid}")
    
    conn.commit(); cur.close(); conn.close()
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    wallet_url = f"https://slh-nft.com/wallet?id={uid}"
    markup.add(KeyboardButton("ًں’ژ ×گ×¨× ×§ SUPREME (×’×¨×¤×™)", web_app=WebAppInfo(url=wallet_url)))
    markup.add("ًں“ٹ ×¤×•×¨×ک×¤×•×œ×™×•", "ًں‘¥ ×”×–×‍×ں ×—×‘×¨×™×‌", "ًں•¹ï¸ڈ ×گ×¨×§×™×™×“", "ًں“‹ ×‍×¦×‘ ×‍×¢×¨×›×ھ")
    
    bot.send_message(message.chat.id, f"ًں’ژ **WELCOME TO DIAMOND SAAS**\n×”×گ×¨× ×§ ×©×œ×ڑ ×‍×•×›×ں ×¢×‌ 1,000 SLH ×‍×ھ× ×”!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "ًں‘¥ ×”×–×‍×ں ×—×‘×¨×™×‌")
def send_ref_link(message):
    uid = message.from_user.id
    ref_link = f"https://t.me/{bot.get_me().username}?start={uid}"
    msg = f"ًںڑ€ **×”×–×‍×ں ×—×‘×¨×™×‌ ×•×”×¨×•×•×— ×›×،×£!**\n\n×¢×œ ×›×œ ×—×‘×¨ ×©×™×¦×ک×¨×£ ×“×¨×ڑ ×”×œ×™× ×§ ×©×œ×ڑ:\nًں’° ×گ×ھ×” ×ھ×§×‘×œ **500 SLH**\nًںژپ ×”×—×‘×¨ ×™×§×‘×œ **200 SLH** ×‘×•× ×•×،!\n\n×”×œ×™× ×§ ×©×œ×ڑ:\n{ref_link}"
    bot.reply_to(message, msg, parse_mode="Markdown")

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    body = (await request.body()).decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(body)])
    return "ok"

@app.on_event("startup")
def on_startup():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

@bot.message_handler(func=lambda m: m.text == "🏆 טבלת אלופים")
def show_leaderboard(message):
    logger.info(f"🏆 LEADERBOARD ACCESSED BY: {message.from_user.id}")
    try:
        conn = get_db(); cur = conn.cursor()
        # שליפת 10 המובילים לפי יתרה
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
        top_users = cur.fetchall()
        cur.close(); conn.close()

        leaderboard_msg = "🏆 **היכל התהילה - Diamond Leaders** 🏆\n"
        leaderboard_msg += "━━━━━━━━━━━━━━━━━━\n\n"
        
        icons = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
        
        for i, user in enumerate(top_users):
            uid, bal = user
            # הסתרת חלק מה-ID לפרטיות
            hidden_id = f"{str(uid)[:4]}***{str(uid)[-2:]}"
            leaderboard_msg += f"{icons[i]} {hidden_id} — **{bal:,} SLH**\n"
            
        leaderboard_msg += "\n━━━━━━━━━━━━━━━━━━\n"
        leaderboard_msg += "🚀 הזמן חברים כדי לעלות בדירוג!"
        
        bot.reply_to(message, leaderboard_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        bot.reply_to(message, "❌ תקלה בטעינת הטבלה.")

# עדכון התפריט הראשי להוספת הכפתור
def main_menu_with_leaderboard(uid):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    wallet_url = f"https://slh-nft.com/wallet?id={uid}"
    markup.add(KeyboardButton("💎 ארנק SUPREME (גרפי)", web_app=WebAppInfo(url=wallet_url)))
    markup.add("📊 פורטפוליו", "🏆 טבלת אלופים")
    markup.add("👥 הזמן חברים", "🕹️ ארקייד", "📋 מצב מערכת")
    return markup

# עדכון פונקציית ה-start שתשתמש בתפריט החדש
@bot.message_handler(commands=['start'])
def start_new(message):
    uid = str(message.from_user.id)
    bot.send_message(message.chat.id, "💎 **DIAMOND SUPREME**", reply_markup=main_menu_with_leaderboard(uid))
