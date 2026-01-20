import logging
import asyncio
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters,
    Defaults
)
from telegram.constants import ParseMode

# טעינת הגדרות ומסד נתונים
from config import BOT_TOKEN
from app.database.manager import db

# ייבוא משחקים
from app.games.dice import (
    start_dice, 
    custom_bet_prompt, 
    pick_number_screen, 
    handle_dice_run, 
    handle_dice_msg_input
)
from app.games.blackjack import start_blackjack # דוגמה למשחקים קיימים
from app.games.crash import start_crash
from app.games.mines import start_mines
from app.games.slots import start_slots
from app.games.roulette import start_roulette

# ייבוא פונקציות בוט כלליות
from app.bot.welcome import start_command

# הגדרת לוגים מקצועית
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: dict):
    """טיפול בשגיאות גלובלי כדי שהבוט לא יקרוס"""
    logger.error(f"Error occurred: {context.error}")

async def main():
    # הגדרת ברירת מחדל ל-Markdown
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
    
    # בניית האפליקציה
    application = ApplicationBuilder().token(BOT_TOKEN).defaults(defaults).build()

    # --- פקודות בסיסיות ---
    application.add_handler(CommandHandler("start", start_command))

    # --- משחק קוביות (Dice) - Handlers משופרים ---
    application.add_handler(CallbackQueryHandler(start_dice, pattern="^play_dice$"))
    application.add_handler(CallbackQueryHandler(custom_bet_prompt, pattern="^dice_custom_bet$"))
    application.add_handler(CallbackQueryHandler(pick_number_screen, pattern="^dice_step2_"))
    application.add_handler(CallbackQueryHandler(handle_dice_run, pattern="^dice_run_"))
    
    # --- משחקים נוספים (שמירה על הקיים) ---
    application.add_handler(CallbackQueryHandler(start_blackjack, pattern="^play_blackjack$"))
    application.add_handler(CallbackQueryHandler(start_crash, pattern="^play_crash$"))
    application.add_handler(CallbackQueryHandler(start_mines, pattern="^play_mines$"))
    application.add_handler(CallbackQueryHandler(start_slots, pattern="^play_slots$"))
    application.add_handler(CallbackQueryHandler(start_roulette, pattern="^play_roulette$"))

    # --- טיפול בקלט טקסט (חשוב להימור מותאם אישית) ---
    # ה-MessageHandler הזה בודק בתוך הפונקציה אם המשתמש במצב "המתנה להימור"
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_dice_msg_input
    ))

    # רישום מנגנון שגיאות
    application.add_error_handler(error_handler)

    # --- הרצת הבוט ---
    print("💎 הבוט הופעל בהצלחה - כל המשחקים מחוברים!")
    await application.run_polling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
