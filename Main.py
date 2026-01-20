import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN

# הגדר logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text("🤖 הבוט עובד! הסירו את ה-Conflict.")

def main():
    print("=" * 50)
    print("🚀 NFTY ULTRA BOT - FIXING CONFLICT")
    print("=" * 50)
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר!")
        return
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    # קבל את משתני הסביבה
    port = int(os.environ.get("PORT", 8080))
    railway_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", None)
    
    # בדוק אם אנחנו ב-Railway
    if railway_public_domain:
        # ב-Railway - השתמש ב-webhooks
        webhook_url = f"https://{railway_public_domain}/{TELEGRAM_TOKEN}"
        
        logger.info(f"🔗 Public Domain: {railway_public_domain}")
        logger.info(f"🌐 Webhook URL: {webhook_url}")
        
        # הגדר webhook
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True,
            secret_token=TELEGRAM_TOKEN
        )
    else:
        # מקומי - השתמש ב-polling
        logger.info("📡 Using polling (local development)...")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
