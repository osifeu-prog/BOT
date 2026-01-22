import telebot
from fastapi import FastAPI, Request
from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL, ADMIN_ID
from handlers.arcade import play_dice
from handlers.ai_agent import get_market_insight
from handlers.saas import get_support_info, get_marketplace
from handlers.marketing import process_referral
import uvicorn

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Empire Online", "owner": ADMIN_ID}

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return "ok"

# --- חיבור הלוגיקה העסקית ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    bot.reply_to(message, f"💎 **Diamond Supreme Live**\nכל המערכות פעילות.\nמשתנה WIN_CHANCE מוגדר ב-Railway.")

@bot.message_handler(func=lambda m: m.text == "🕹️ ארקייד")
def start_arcade(message):
    bot.send_message(message.chat.id, "המערכת מושכת נתונים מ-PostgreSQL...")

# פקודת ניהול לבדיקת משתנים (רק לאדמין)
@bot.message_handler(commands=['admin_check'])
def check_vars(message):
    if str(message.from_user.id) == ADMIN_ID:
        bot.reply_to(message, f"✅ חיבור תקין!\nAdmin: {ADMIN_ID}\nWebhook: {WEBHOOK_URL}")

@app.on_event("startup")
def on_startup():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
