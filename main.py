"""Main application entry point"""
import asyncio
import logging
from telegram import Update
from bot.bot_instance import create_application
from bot.database import init_db
from bot.background_tasks import start_background_tasks
from bot.config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main application startup"""
    logger.info("🚀 Starting Ultimate Casino Bot...")
    
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return
    
    await init_db()
    application = create_application()
    asyncio.create_task(start_background_tasks())
    
    if config.WEBHOOK_URL:
        logger.info(f"🌐 Starting webhook on port {config.PORT}")
        await application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path="",
            webhook_url=config.WEBHOOK_URL
        )
    else:
        logger.info("📡 Starting polling mode")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main())
