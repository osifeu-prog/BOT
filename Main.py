#!/usr/bin/env python3
"""
NFTY ULTRA - ABSOLUTELY NO CONFLICT
גרסה סופית שתמנע קונפליקטים בשום מצב.
"""

import os
import sys
import asyncio
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# כבה לוגים לחלוטין
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# רק הודעות חשובות שלנו
print = lambda *args, **kwargs: __builtins__.print("🚀", *args, **kwargs)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎰 NFTY ULTRA CASINO - הבוט פעיל!")

def delete_webhook_completely(token: str):
    """מוחק webhook בצורה אגרסיבית"""
    import requests
    
    print("🧹 מנקה webhook ישן לחלוטין...")
    
    # נסה עד 3 פעמים
    for i in range(3):
        try:
            url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            response = requests.get(url, params={"drop_pending_updates": "true"}, timeout=10)
            if response.status_code == 200:
                print(f"✅ Webhook נמחק (נסיון {i+1})")
            time.sleep(1)
        except:
            pass
    
    # בדוק שאין webhook
    try:
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("result", {}).get("url"):
                print("⚠️  עדיין יש webhook - נמחק שוב")
                # נמחק שוב
                url = f"https://api.telegram.org/bot{token}/deleteWebhook"
                requests.get(url, params={"drop_pending_updates": "true"}, timeout=5)
    except:
        pass

def main():
    """הנקודה הראשית - פשוטה וחזקה"""
    print("NFTY ULTRA BOT - הפעלה")
    
    # טען טוקן
    try:
        from config import TELEGRAM_TOKEN
    except:
        print("❌ לא ניתן לטעון config.py")
        sys.exit(1)
    
    token = TELEGRAM_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ טוקן לא תקין")
        sys.exit(1)
    
    print(f"טוקן: {token[:10]}...")
    
    # קבל פורט
    port = int(os.environ.get("PORT", 8080))
    
    # בדוק אם אנחנו ב-Railway (לפי משתנים)
    is_railway = False
    domain = None
    
    if os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
        is_railway = True
        domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    elif os.environ.get("PORT"):
        # אם יש PORT סביר שאנחנו ב-Railway
        is_railway = True
        # ננסה למצוא דומיין
        service_name = os.environ.get("RAILWAY_SERVICE_NAME", "bot")
        domain = f"{service_name}.up.railway.app"
    
    if is_railway:
        print(f"🔧 Railway mode - פורט {port}")
        
        # נקה webhook לחלוטין
        delete_webhook_completely(token)
        
        # צור אפליקציה
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        
        # המתן קצת
        time.sleep(2)
        
        # הגדר webhook
        domain = domain.replace("https://", "").replace("http://", "").rstrip("/")
        webhook_url = f"https://{domain}/{token}"
        
        print(f"🌐 מגדיר webhook: {webhook_url}")
        
        async def run():
            await app.initialize()
            
            # הגדר webhook
            await app.bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            # הפעל webhook
            await app.start()
            await app.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=token,
                webhook_url=webhook_url,
                drop_pending_updates=True
            )
            
            print("✅ הבוט פועל עם webhook!")
            
            # החזק את התוכנית רצה
            await asyncio.Event().wait()
        
        # הרץ
        asyncio.run(run())
    else:
        print("💻 מקומי - polling")
        
        # נקה webhook
        delete_webhook_completely(token)
        
        # צור אפליקציה
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        
        # המתן
        time.sleep(2)
        
        # הרץ polling
        print("🔄 מפעיל polling...")
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )

if __name__ == "__main__":
    main()
