import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# הגדר logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text("🎰 NFTY ULTRA CASINO - הבוט פועל!")

def main():
    print("=" * 60)
    print("🚀 NFTY ULTRA BOT - Railway Deployment")
    print("=" * 60)
    
    from config import TELEGRAM_TOKEN
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר!")
        return
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    # בדוק אם אנחנו ב-Railway
    port = int(os.environ.get("PORT", 8080))
    railway_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", None)
    
    if railway_public_domain:
        # ב-Railway - השתמש ב-webhooks
        webhook_url = f"https://{railway_public_domain}/{TELEGRAM_TOKEN}"
        logger.info(f"🌐 Railway Webhook: {webhook_url}")
        
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # מקומי - השתמש ב-polling
        logger.info("📡 Local Polling")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
