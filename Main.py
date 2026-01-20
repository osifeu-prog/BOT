import os
import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    Defaults
)
from telegram.constants import ParseMode

# ייבוא לוגיקה מהקבצים הקיימים
from database import get_user_profile
from mines import start_mines, handle_mine_click
from payment_flow import handle_payment_screenshot, send_broadcast
from admin_panel import admin_main

# הגדרות לוגים
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# משתני סביבה חובה
TOKEN = os.getenv("TELEGRAM_TOKEN")
# ה-URL של האפליקציה ב-Railway (למשל: https://nfty-production.up.railway.app)
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
# פורט ש-Railway מקצה אוטומטית (ברירת מחדל 8080)
PORT = int(os.getenv("PORT", 8080))

async def post_init(application):
    """הגדרות הרצה ראשוניות"""
    commands = [
        BotCommand("start", "🏠 תפריט ראשי"),
        BotCommand("profile", "📊 הפרופיל שלי")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Webhook system initialized.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # הפונקציה המקורית שלך נשארת כאן (ללא שינוי לוגי)
    # ... (קוד ה-start מהגרסה הקודמת)
    pass

if __name__ == '__main__':
    if not WEBHOOK_URL:
        raise ValueError("Missing WEBHOOK_URL! Please set it in Railway variables.")

    defaults = Defaults(parse_mode=ParseMode.HTML)
    
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .defaults(defaults)
        .post_init(post_init)
        .build()
    )

    # רישום Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", send_broadcast))
    application.add_handler(CallbackQueryHandler(start, pattern="^nav_home$"))
    application.add_handler(CallbackQueryHandler(start_mines, pattern="^game_mines$"))
    application.add_handler(CallbackQueryHandler(handle_mine_click, pattern="^mine_"))
    application.add_handler(CallbackQueryHandler(admin_main, pattern="^admin_main$"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))

    # הגדרת הרצה בפורמט Webhook
    logger.info(f"🚀 Starting Webhook on port {PORT}...")
    
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN, # שימוש בטוקן כנתיב סודי לאבטחה
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
