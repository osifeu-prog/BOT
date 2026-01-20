"""Bot application"""
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .config import config
from .handlers import (
    start, help_command, balance, language,
    casino_menu, investment_menu, shop_menu,
    referral_info, admin_panel, handle_callback
)
import logging

logger = logging.getLogger(__name__)

def create_application():
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("casino", casino_menu))
    app.add_handler(CommandHandler("invest", investment_menu))
    app.add_handler(CommandHandler("shop", shop_menu))
    app.add_handler(CommandHandler("referral", referral_info))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("✅ Bot configured")
    return app
