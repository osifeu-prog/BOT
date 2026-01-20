#!/usr/bin/env python3
"""
NFTY ULTRA BOT - RAILWAY OPTIMIZED
גרסה מותאמת במיוחד ל-Railway עם webhook בלבד
"""

import os
import sys
import logging
import time
from telegram.ext import Application, CommandHandler
import asyncio

# השתק הכל
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

logging.basicConfig(
    format='NFTY ULTRA - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    """פקודת /start"""
    await update.message.reply_text("🎰 NFTY ULTRA CASINO - הבוט פועל ב-Railway!")

async def help_command(update, context):
    """פקודת /help"""
    await update.message.reply_text("📖 פקודות זמינות:\n/start - התחל\n/help - עזרה")

def cleanup_webhook(token):
    """נקוי webhook ישן - חשוב מאוד!"""
    import requests
    
    print("🧹 נקוי webhook ישן...")
    
    # נסיון 1: מחיקת webhook
    try:
        delete_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        response = requests.get(delete_url, params={"drop_pending_updates": "true"}, timeout=10)
        print(f"🗑️  מחיקת webhook: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('description', 'נמחק')}")
    except Exception as e:
        print(f"⚠️  לא הצלחנו למחוק webhook: {e}")
    
    # נסיון 2: בדיקה מה יש כרגע
    try:
        get_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(get_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                webhook_info = data.get("result", {})
                if webhook_info.get("url"):
                    print(f"⚠️  עדיין יש webhook פעיל: {webhook_info.get('url')[:50]}...")
    except Exception as e:
        print(f"⚠️  לא ניתן לבדוק webhook: {e}")

def is_railway_environment():
    """בדיקה אם אנחנו ב-Railway"""
    railway_vars = [
        "RAILWAY_PUBLIC_DOMAIN",
        "RAILWAY_STATIC_URL", 
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_SERVICE_NAME"
    ]
    
    for var in railway_vars:
        if os.environ.get(var):
            return True
    return False

async def setup_webhook(app, token, domain, port):
    """הגדרת webhook ל-Railway"""
    try:
        # קודם כל, נמחק webhook קיים
        import requests
        delete_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        requests.get(delete_url, params={"drop_pending_updates": "true"}, timeout=5)
        
        # נחכה קצת
        await asyncio.sleep(1)
        
        # עכשיו נגדיר webhook חדש
        webhook_url = f"https://{domain}/{token}"
        print(f"🌐 הגדרת Webhook URL: {webhook_url}")
        
        # נגדיר את ה-webhook דרך ה-Application
        await app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            secret_token=token[:32]
        )
        
        print("✅ Webhook הוגדר בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בהגדרת webhook: {e}")
        return False

async def main_async():
    """נקודת כניסה ראשית - async version"""
    print("=" * 70)
    print("🚀 NFTY ULTRA BOT - RAILWAY EDITION")
    print("=" * 70)
    print(f"🕐 התחלה: {time.strftime('%H:%M:%S')}")
    
    # שלב 1: טעינת הטוקן
    try:
        from config import TELEGRAM_TOKEN
    except ImportError:
        print("❌ config.py לא נמצא")
        sys.exit(1)
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_TOKEN לא הוגדר!")
        print("   ערוך את config.py או הגדר משתנה סביבה")
        sys.exit(1)
    
    print(f"✅ טוקן: {TELEGRAM_TOKEN[:10]}...")
    
    # שלב 2: בדיקת סביבה
    port = int(os.environ.get("PORT", 8080))
    print(f"🔧 פורט: {port}")
    
    # שלב 3: נקוי webhook ישן
    cleanup_webhook(TELEGRAM_TOKEN)
    
    # שלב 4: הפעלת הבוט
    try:
        # בניית האפליקציה
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # הוספת handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        
        # בדיקה אם אנחנו ב-Railway
        if is_railway_environment():
            print("🏗️  סביבת Railway זוהתה")
            
            # חובה להשתמש ב-webhook ב-Railway
            domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
            if not domain:
                # נסיון לשחזר דומיין
                service_name = os.environ.get("RAILWAY_SERVICE_NAME", "bot")
                domain = f"{service_name}.up.railway.app"
                print(f"🌐 דומיין משוער: {domain}")
            
            # נקה את הדומיין
            if domain.startswith("https://"):
                domain = domain.replace("https://", "")
            elif domain.startswith("http://"):
                domain = domain.replace("http://", "")
            domain = domain.rstrip("/")
            
            print(f"🎯 שימוש ב-webhook עם דומיין: {domain}")
            
            # הגדר webhook
            webhook_set = await setup_webhook(app, TELEGRAM_TOKEN, domain, port)
            if not webhook_set:
                print("⚠️  לא הצלחנו להגדיר webhook, מנסה להמשיך בכל זאת...")
            
            # הפעל את ה-webhook server
            print(f"🚀 מפעיל שרת webhook על port {port}...")
            
            await app.initialize()
            await app.start()
            
            # הפעל את ה-webhook listener
            await app.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_TOKEN,
                webhook_url=f"https://{domain}/{TELEGRAM_TOKEN}",
                drop_pending_updates=True
            )
            
            print("✅ הבוט פועל עם webhook ב-Railway!")
            print("🔄 מחכה להודעות...")
            
            # שמור את האפליקציה פעילה
            await asyncio.Event().wait()
            
        else:
            # סביבה מקומית - polling
            print("💻 הרצה עם polling (סביבה מקומית)")
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            print("✅ הבוט פועל עם polling!")
            print("🔄 מחכה להודעות...")
            
            # שמור את האפליקציה פעילה
            await asyncio.Event().wait()
            
    except Exception as e:
        print(f"❌ שגיאה קשה: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """נקודת כניסה ראשית"""
    # הפעל את האפליקציה
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
