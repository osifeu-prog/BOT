import os
import logging
import asyncio
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

# הגדרת לוגים ברמה גבוהה יותר
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# טעינת משתני סביבה עם וולידציה
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN missing in environment variables!")

async def post_init(application):
    """הגדרות שרצות מיד עם עליית הבוט"""
    commands = [
        BotCommand("start", "🏠 תפריט ראשי"),
        BotCommand("profile", "📊 הפרופיל שלי"),
        BotCommand("help", "❓ עזרה ותמיכה")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set successfully.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בפקודת הסטארט עם טיפול בשגיאות מובנה"""
    try:
        user = update.effective_user
        query = update.callback_query
        
        # עדכון/שליפת פרופיל
        profile = get_user_profile(user.id)
        
        balance = int(profile.get('balance', 0))
        stocks = profile.get('stocks', 0)
        tier = profile.get('tier', 'Regular')

        welcome_text = (
            f"👑 <b>ברוכים הבאים ל-NFTY MADNESS</b> 👑\n\n"
            f"👤 שחקן: <code>{user.first_name}</code>\n"
            f"💰 יתרה: <b>{balance:,} 🪙</b>\n"
            f"📈 מניות: <b>{stocks}</b>\n"
            f"🏆 דרגה: <b>{tier}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎮 בחר משחק או פעולה מהתפריט למטה:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🎮 משחק מוקשים", callback_data="game_mines"),
                InlineKeyboardButton("💹 בורסה", callback_data="nav_market")
            ],
            [
                InlineKeyboardButton("💎 הפקדה (AI)", callback_data="nav_shop"),
                InlineKeyboardButton("📊 פרופיל", callback_data="nav_profile")
            ],
            [InlineKeyboardButton("❓ עזרה ומדריכים", callback_data="nav_help")]
        ]
        
        if str(user.id) == ADMIN_ID:
            keyboard.append([InlineKeyboardButton("⚙️ פאנל ניהול אדמין", callback_data="admin_main")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.answer() # מונע את "השעון" על הכפתור בטלגרם
            await query.edit_message_text(welcome_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        error_msg = "❌ אירעה שגיאה בטעינת הנתונים. נסה שוב מאוחר יותר."
        if query:
            await query.message.reply_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

if __name__ == '__main__':
    # הגדרת ברירת מחדל ל-ParseMode כדי לא לחזור על HTML בכל פונקציה
    defaults = Defaults(parse_mode=ParseMode.HTML)
    
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .defaults(defaults)
        .post_init(post_init) # הרצת פונקציית הגדרות ראשוניות
        .build()
    )
    
    # --- רישום Handlers ---
    
    # פקודות ישירות
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", send_broadcast))
    
    # ניווט ומשחקים
    application.add_handler(CallbackQueryHandler(start, pattern="^nav_home$"))
    application.add_handler(CallbackQueryHandler(start_mines, pattern="^game_mines$"))
    application.add_handler(CallbackQueryHandler(handle_mine_click, pattern="^mine_"))
    application.add_handler(CallbackQueryHandler(admin_main, pattern="^admin_main$"))
    
    # טיפול בהפקדות (תמונות)
    # הוספת כמות ניסיונות והגבלת גודל קובץ במידת הצורך
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))
    
    # טיפול בשגיאות גלובלי
    # application.add_error_handler(error_handler_function) 

    logger.info("🚀 NFTY Madness is starting polling...")
    application.run_polling(drop_pending_updates=True)
