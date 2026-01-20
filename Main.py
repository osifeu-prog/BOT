import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
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

# ייבוא לוגיקה עסקית
from database import get_user_profile, update_user_stat, get_market_price
from mines import start_mines, handle_mine_click
from payment_flow import handle_payment_screenshot, send_broadcast
from admin_panel import admin_main

# הגדרות לוגים
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# טעינת משתנים מ-Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # חייב להיות בפורמט https://your-app.up.railway.app
PORT = int(os.getenv("PORT", 8080))

async def post_init(application):
    """הגדרות תפריט פקודות בטלגרם מיד עם העלייה"""
    await application.bot.set_my_commands([
        BotCommand("start", "🏠 תפריט ראשי"),
        BotCommand("profile", "📊 הפרופיל שלי"),
        BotCommand("broadcast", "📢 הודעה גלובלית (אדמין)")
    ])
    logger.info("Webhook system ready.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """תפריט ראשי מעוצב ומקצועי"""
    user = update.effective_user
    profile = get_user_profile(user.id)
    
    # וידוא שקיימת יתרה (למניעת שגיאות None)
    balance = int(profile.get('balance', 0))
    
    welcome_text = (
        f"👑 <b>NFTY MADNESS CASINO</b> 👑\n\n"
        f"👤 שחקן: <code>{user.first_name}</code>\n"
        f"💰 יתרה: <b>{balance:,} 🪙</b>\n"
        f"🏆 דרגה: <b>{profile.get('tier', 'Regular')}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎰 בחר פעולה מהתפריט:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 משחק מוקשים", callback_data="game_mines"),
         InlineKeyboardButton("💹 בורסה", callback_data="nav_market")],
        [InlineKeyboardButton("💎 הפקדה אוטומטית (AI)", callback_data="nav_shop")],
        [InlineKeyboardButton("📊 פרופיל מלא", callback_data="nav_profile")]
    ]
    
    if str(user.id) == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ פאנל ניהול", callback_data="admin_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    if not TOKEN or not WEBHOOK_URL:
        logger.error("Missing TOKEN or WEBHOOK_URL!")
        exit(1)

    # הגדרות ברירת מחדל
    defaults = Defaults(parse_mode=ParseMode.HTML)
    
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .defaults(defaults)
        .post_init(post_init)
        .build()
    )
    
    # רישום פקודות ולחיצות
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", send_broadcast))
    
    application.add_handler(CallbackQueryHandler(start, pattern="^nav_home$"))
    application.add_handler(CallbackQueryHandler(start_mines, pattern="^game_mines$"))
    application.add_handler(CallbackQueryHandler(handle_mine_click, pattern="^mine_"))
    application.add_handler(CallbackQueryHandler(admin_main, pattern="^admin_main$"))
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))
    
    # הרצת ה-Webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN, # אבטחה: רק טלגרם יודעת את הנתיב הזה
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
