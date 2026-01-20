#!/usr/bin/env python3
"""
NFTY ULTRA BOT - Railway Optimized
גרסה שפועלת עם webhook בלבד ב-Railway, ומניעה קונפליקטים.
"""

import os
import sys
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# כבה logging מיותר
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# הגדר logging בסיסי
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# פקודות
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """שלח הודעת ברוכים הבאים"""
    await update.message.reply_text('🎰 ברוך הבא ל-NFTY ULTRA BOT!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """שלח הודעת עזרה"""
    await update.message.reply_text('לחץ /start כדי להתחיל.')

def is_railway():
    """בדוק אם אנחנו ב-Railway"""
    # ב-Railway יש משתנה סביבה PORT תמיד
    if os.environ.get('PORT'):
        return True
    # או משתנים אחרים של Railway
    railway_vars = ['RAILWAY_PUBLIC_DOMAIN', 'RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT']
    for var in railway_vars:
        if os.environ.get(var):
            return True
    return False

async def setup_webhook(app: Application, token: str, url: str):
    """הגדר webhook והסר כל הגדרה קודמת"""
    # קודם כל, מחק webhook קיים
    delete_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    try:
        import requests
        response = requests.get(delete_url, params={'drop_pending_updates': True}, timeout=10)
        logger.info(f"Deleted old webhook: {response.status_code}")
    except Exception as e:
        logger.warning(f"Could not delete old webhook: {e}")
    
    # המתן קצת
    await asyncio.sleep(1)
    
    # עכשיו הגדר webhook חדש
    await app.bot.set_webhook(
        url=url,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        secret_token=token[:32]  # secret token להגנה
    )
    logger.info(f"Webhook set to: {url}")

async def run_webhook(app: Application, port: int, token: str, public_url: str):
    """הרץ את הבוט עם webhook"""
    # הגדר את ה-webhook
    webhook_url = f"{public_url}/{token}"
    await setup_webhook(app, token, webhook_url)
    
    # הרץ את שרת ה-webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,
        webhook_url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

async def run_polling(app: Application):
    """הרץ את הבוט עם polling (לסביבה מקומית)"""
    # מחק כל webhook קודם כדי למנוע קונפליקטים
    delete_url = f"https://api.telegram.org/bot{app.bot.token}/deleteWebhook"
    try:
        import requests
        response = requests.get(delete_url, params={'drop_pending_updates': True}, timeout=10)
        logger.info(f"Deleted webhook for polling: {response.status_code}")
    except Exception as e:
        logger.warning(f"Could not delete webhook: {e}")
    
    # המתן קצת
    await asyncio.sleep(2)
    
    # התחל polling
    await app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        pool_timeout=10  # זמן קצר יותר
    )

def main():
    """נקודת כניסה ראשית"""
    print("=" * 60)
    print("🚀 NFTY ULTRA BOT - Starting...")
    print("=" * 60)
    
    # טען את הטוקן
    try:
        from config import TELEGRAM_TOKEN
    except ImportError:
        print("❌ Error: config.py not found")
        sys.exit(1)
    
    token = TELEGRAM_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Error: TELEGRAM_TOKEN not set")
        sys.exit(1)
    
    print(f"✅ Token loaded: {token[:10]}...")
    
    # בדוק אם אנחנו ב-Railway
    PORT = int(os.environ.get('PORT', 8080))
    RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    
    print(f"🔧 Port: {PORT}")
    print(f"🌐 Railway Public Domain: {RAILWAY_PUBLIC_DOMAIN or 'Not set'}")
    
    # בנה את האפליקציה
    app = Application.builder().token(token).build()
    
    # הוסף handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # הרץ בהתאם לסביבה
    if is_railway():
        print("🏗️  Running in Railway mode (webhook only)")
        
        if not RAILWAY_PUBLIC_DOMAIN:
            # נסה לשחזר את הדומיין
            RAILWAY_SERVICE_NAME = os.environ.get('RAILWAY_SERVICE_NAME', 'bot')
            RAILWAY_PUBLIC_DOMAIN = f"{RAILWAY_SERVICE_NAME}.up.railway.app"
            print(f"⚠️  Using inferred domain: {RAILWAY_PUBLIC_DOMAIN}")
        
        # ודא שהדומיין מתחיל עם https://
        if not RAILWAY_PUBLIC_DOMAIN.startswith('https://'):
            RAILWAY_PUBLIC_DOMAIN = f"https://{RAILWAY_PUBLIC_DOMAIN}"
        
        # הרץ עם webhook
        asyncio.run(run_webhook(app, PORT, token, RAILWAY_PUBLIC_DOMAIN))
    else:
        print("💻 Running in local mode (polling)")
        # הרץ עם polling
        asyncio.run(run_polling(app))

if __name__ == '__main__':
    main()
