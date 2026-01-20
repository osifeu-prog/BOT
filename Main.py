#!/usr/bin/env python3
"""
NFTY ULTRA - NO CONFLICT SOLUTION
גרסה פשוטה שפועלת בלי קונפליקטים
"""

import os
import sys
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# השתק הכל
import logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

# פקודות בסיסיות
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎰 NFTY ULTRA BOT - פעיל!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("לחץ על /start להתחיל")

def delete_old_webhook(token: str):
    """מוחק webhook קיים - חשוב מאוד!"""
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        params = {"drop_pending_updates": "true"}
        response = requests.get(url, params=params, timeout=10)
        print("🗑️  Webhook ישן נמחק")
    except:
        pass

def main():
    print("=" * 60)
    print("🚀 NFTY ULTRA BOT - אתחול...")
    print("=" * 60)
    
    # טעינת הטוקן
    try:
        from config import TELEGRAM_TOKEN
    except ImportError:
        print("❌ config.py לא נמצא")
        sys.exit(1)
    
    token = TELEGRAM_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_TOKEN לא הוגדר")
        sys.exit(1)
    
    print(f"✅ טוקן: {token[:10]}...")
    
    # מחיקת webhook קיים
    delete_old_webhook(token)
    
    # בדיקת Railway
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🌐 דומיין: {domain or 'לא נמצא'}")
    print(f"🔧 פורט: {port}")
    
    # בניית האפליקציה
    app = Application.builder().token(token).build()
    
    # הוספת פקודות
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # הרצה
    if domain:
        # ב-Railway - חייבים webhook
        domain = domain.replace("https://", "").replace("http://", "").rstrip("/")
        webhook_url = f"https://{domain}/{token}"
        
        print(f"\n🎯 Webhook URL: {webhook_url}")
        print("🏗️  מפעיל ב-Railway mode...")
        
        async def run_webhook():
            await app.initialize()
            await app.bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            await app.start()
            await app.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=token,
                webhook_url=webhook_url,
                drop_pending_updates=True
            )
            print("✅ הבוט פועל עם webhook!")
            await asyncio.Event().wait()  # מחכה לנצח
            
        asyncio.run(run_webhook())
    else:
        # מקומי - polling
        print("\n💻 מפעיל ב-local mode...")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
