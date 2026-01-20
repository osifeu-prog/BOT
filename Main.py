#!/usr/bin/env python3
"""
NFTY ULTRA BOT - RAILWAY WEBHOOK ONLY
גרסה שמשתמשת רק ב-webhook ב-Railway, ללא אפשרות של polling כלל.
"""

import os
import sys
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# השתק לוגים לא חשובים
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

logging.basicConfig(
    format='NFTY ULTRA - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text("🎰 NFTY ULTRA CASINO - הבוט פועל ב-Railway!")

async def help_command(update, context):
    await update.message.reply_text("📖 פקודות זמינות:\n/start - התחל\n/help - עזרה")

async def echo(update, context):
    """פשוט הד בחזרה"""
    await update.message.reply_text(f"קבלתי: {update.message.text}")

def get_domain():
    """מחזיר את הדומיין של Railway"""
    # בדוק אם אנחנו ב-Railway
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    if not domain:
        # נסה לשחזר משתנים אחרים
        domain = os.environ.get("RAILWAY_STATIC_URL")
    if not domain:
        # אם לא, השתמש בשם השירות
        service_name = os.environ.get("RAILWAY_SERVICE_NAME", "bot")
        domain = f"{service_name}.up.railway.app"
    
    # נקה את הדומיין
    if domain.startswith("https://"):
        domain = domain.replace("https://", "")
    elif domain.startswith("http://"):
        domain = domain.replace("http://", "")
    domain = domain.rstrip("/")
    
    return domain

async def main():
    print("=" * 70)
    print("🚀 NFTY ULTRA BOT - RAILWAY WEBHOOK EDITION")
    print("=" * 70)
    
    # טעינת הטוקן
    try:
        from config import TELEGRAM_TOKEN
    except ImportError:
        print("❌ config.py לא נמצא")
        sys.exit(1)
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_TOKEN לא הוגדר!")
        sys.exit(1)
    
    print(f"✅ טוקן: {TELEGRAM_TOKEN[:10]}...")
    
    # חובה להשתמש ב-webhook ב-Railway
    domain = get_domain()
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🌐 דומיין: {domain}")
    print(f"🔧 פורט: {port}")
    
    # בניית האפליקציה
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # הוספת handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # הגדרת webhook
    webhook_url = f"https://{domain}/{TELEGRAM_TOKEN}"
    print(f"🎯 Webhook URL: {webhook_url}")
    
    try:
        # התחל את האפליקציה
        await app.initialize()
        
        # הגדר webhook
        await app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            secret_token=TELEGRAM_TOKEN[:32]
        )
        
        print("✅ Webhook הוגדר בהצלחה!")
        
        # הפעל את שרת ה-webhook
        await app.start()
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
        
        print("🚀 הבוט פועל עם webhook ב-Railway!")
        print("🔄 מחכה להודעות...")
        
        # שמור את האפליקציה פעילה לנצח
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
