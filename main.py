# -*- coding: utf-8 -*-
import logging
import sys
import os

# הגדרת לוגים מפורטת שתופיע ב-Railway
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("🚀 Starting SLH OS Debug Mode...")

# תיקון הדרייבר של PostgreSQL (Monkey Patch)
try:
    import psycopg2_binary
    import sys
    sys.modules['psycopg2'] = psycopg2_binary
    logger.info("✅ Psycopg2 monkey patch applied successfully")
except Exception as e:
    logger.error(f"❌ Failed to patch psycopg2: {e}")

try:
    logger.info("📦 Importing modules...")
    import telebot
    from fastapi import FastAPI, Request
    from utils.config import TELEGRAM_TOKEN, WEBHOOK_URL
    from handlers import wallet_logic, saas, router, admin
    import uvicorn
    logger.info("✅ All modules imported successfully")
except Exception as e:
    logger.critical(f"💥 IMPORT ERROR: {e}", exc_info=True)
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info(f"🌐 Setting Webhook to: {WEBHOOK_URL}")
    try:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        logger.info("✅ Webhook set successfully")
    except Exception as e:
        logger.error(f"❌ Webhook setup failed: {e}")

@app.post("/")
async def process_webhook(request: Request):
    logger.debug("📩 Received webhook request")
    json_string = await request.body()
    update = telebot.types.Update.de_json(json_string.decode('utf-8'))
    bot.process_new_updates([update])
    return {"status": "ok"}

@app.get("/")
def health_check():
    logger.debug("💓 Health check pinged")
    return {"status": "Online"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🔥 Uvicorn starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
