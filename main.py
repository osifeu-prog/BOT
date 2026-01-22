import telebot
from fastapi import FastAPI, Request
from utils.config import TELEGRAM_TOKEN, DATABASE_URL, WEBHOOK_URL
import uvicorn

# אתחול הבוט (ללא Polling!)
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Diamond Supreme Empire is Online", "webhook": WEBHOOK_URL}

@app.post(f"/{TELEGRAM_TOKEN}/")
async def process_webhook(request: Request):
    if request.headers.get('content-type') == 'application/json':
        json_string = await request.body()
        update = telebot.types.Update.de_json(json_string.decode('utf-8'))
        bot.process_new_updates([update])
        return {"status": "ok"}
    return {"status": "error"}, 403

# --- כאן יבואו כל ה-Handlers שכתבנו קודם (Start, Arcade, וכו') ---
# (הבוט כבר מכיר אותם כי הם רשומים ב-Decorator של ה-bot)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "💎 **DIAMOND SUPREME (Webhook Mode)**\nהמערכת פעילה ומאובטחת.")

# פונקציה להגדרת ה-Webhook בטלגרם בזמן עלייה
@app.on_event("startup")
def on_startup():
    webhook_path = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}/"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_path)
    print(f"✅ Webhook set to: {webhook_path}")

if __name__ == "__main__":
    # הרצה מקומית לצורך בדיקות (ב-Railway זה ירוץ דרך uvicorn)
    uvicorn.run(app, host="0.0.0.0", port=8000)
