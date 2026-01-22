"""
main.py
=======
The core entry point of the bot.
"""

# --- שלב 1: תיקון תאימות ל-Python 3.13 (למניעת קריסה ב-Railway) ---
import sys
try:
    import imghdr
except ImportError:
    import pure_imghdr
    sys.modules['imghdr'] = pure_imghdr

import logging
import asyncio
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ייבוא הגדרות וראוטרים מהפרויקט שלך
from config import BOT_TOKEN
from handlers.callback_router import handle_callback
from handlers.slots import play_slots  # וודא שהפונקציה קיימת ב-handlers

# הגדרת לוגים מקצועית
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# יצירת אפליקציית FastAPI (לצורך ה-Webhook ב-Railway)
app = FastAPI()

# יצירת אפליקציית הטלגרם
tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- פונקציית טיפול בשגיאות גלובלית (שדרוג חוסן) ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """לוכד שגיאות ומונע קריסה של הבוט."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ קרתה שגיאה פנימית בבוט. הצוות הטכני עודכן."
        )

# --- רישום פקודות וראוטרים ---
def setup_handlers(application):
    # הוספת מטפל השגיאות
    application.add_error_handler(error_handler)
    
    # פקודות בסיס
    # application.add_handler(CommandHandler("start", start_handler)) # הוסף אם קיים
    
    # חיבור הראוטר המרכזי של ה-Callbacks (כולל הסלוטס)
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(handle_callback))

# הגדרת המערכת
setup_handlers(tg_app)

@app.on_event("startup")
async def startup_event():
    """הפעלת הבוט במקביל לשרת ה-Web."""
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()
    logger.info("--- Bot is officially Online! ---")

@app.on_event("shutdown")
async def shutdown_event():
    """סגירה בטוחה של המשאבים."""
    await tg_app.updater.stop()
    await tg_app.stop()
    await tg_app.shutdown()
    logger.info("--- Bot shut down safely ---")

@app.get("/")
async def root():
    return {"status": "running", "version": "2.0.0-pro"}
