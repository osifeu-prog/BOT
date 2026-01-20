import os
import sys
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# השתק לוגים מיותרים
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# הגדר logging לבוט שלנו
logging.basicConfig(
    format='%(asctime)s - NFTY ULTRA - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    """פקודת /start פשוטה"""
    await update.message.reply_text(
        "🎰 **NFTY ULTRA CASINO** 🎰\n\n"
        "✅ הבוט פועל ומוכן!\n\n"
        "🚀 המשחקים זמינים בקרוב..."
    )

def delete_existing_webhook(token):
    """מחיקת webhook קיים - חיוני למניעת קונפליקט"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Webhook קיים נמחק")
            return True
        else:
            logger.warning(f"⚠️ לא ניתן למחוק webhook: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ שגיאה במחיקת webhook: {e}")
        return False

def get_railway_domain():
    """קבלת דומיין מ-Railway - בדיקה לכל האפשרויות"""
    # כל המשתנים האפשריים ב-Railway
    possible_domains = [
        os.environ.get("RAILWAY_PUBLIC_DOMAIN"),
        os.environ.get("RAILWAY_STATIC_URL"),
        os.environ.get("RAILWAY_SERVICE_NAME") + ".railway.internal",
        os.environ.get("RAILWAY_SERVICE_NAME") + ".up.railway.app",
    ]
    
    for domain in possible_domains:
        if domain:
            # ניקוי URL אם יש פרוטוקול
            if domain.startswith("https://"):
                domain = domain.replace("https://", "")
            elif domain.startswith("http://"):
                domain = domain.replace("http://", "")
            
            # הסרת / בסוף
            domain = domain.rstrip("/")
            return domain
    
    return None

def main():
    """נקודת כניסה ראשית"""
    print("=" * 70)
    print("🚀 NFTY ULTRA BOT - ULTIMATE WEBHOOK FIX")
    print("=" * 70)
    
    # טען את הטוקן
    try:
        from config import TELEGRAM_TOKEN
    except ImportError:
        logger.error("❌ config.py לא נמצא או לא תקין")
        sys.exit(1)
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר!")
        print("⚠️ אנא הגדר את TELEGRAM_TOKEN ב-Railway Variables")
        print("📋 צעדים:")
        print("   1. ב-Railway Dashboard → BOT1 → Variables")
        print("   2. לחץ 'New Variable'")
        print("   3. שם: TELEGRAM_TOKEN")
        print("   4. ערך: הטוקן האמיתי שלך מהבוט")
        sys.exit(1)
    
    print(f"✅ טוקן תקין: {TELEGRAM_TOKEN[:10]}...")
    
    # שלב 1: מחיקת webhook קיים - קריטי!
    print("🗑️  מוחק webhook קיים...")
    delete_existing_webhook(TELEGRAM_TOKEN)
    
    # בדיקת סביבה
    port = int(os.environ.get("PORT", 8080))
    print(f"🔧 פורט: {port}")
    
    # בדיקה אם אנחנו ב-Railway
    is_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT") or 
                      os.environ.get("RAILWAY_SERVICE_NAME") or 
                      os.environ.get("PORT"))
    
    # קבלת דומיין
    domain = get_railway_domain()
    
    print(f"🌐 מצב: {'RAILWAY' if is_railway else 'LOCAL'}")
    print(f"🔗 דומיין: {domain if domain else 'לא נמצא'}")
    
    # חייבים webhook ב-Railway!
    if is_railway and domain:
        # מצב PRODUCTION עם webhook
        print(f"🚀 מפעיל ב-webhook mode...")
        
        webhook_url = f"https://{domain}/{TELEGRAM_TOKEN}"
        print(f"🔗 Webhook URL: {webhook_url}")
        
        try:
            # צור אפליקציה
            app = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # הוסף handlers
            app.add_handler(CommandHandler("start", start))
            
            # הפעל עם webhook
            app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_TOKEN,
                webhook_url=webhook_url,
                secret_token=TELEGRAM_TOKEN[:32],
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
        except Exception as e:
            print(f"❌ שגיאת webhook: {e}")
            print("🔄 מנסה עם polling כגיבוי...")
            # נסה עם polling
            app = Application.builder().token(TELEGRAM_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.run_polling(drop_pending_updates=True)
    
    elif is_railway and not domain:
        # ב-Railway אבל אין דומיין - יצירת דומיין אוטומטי
        print("⚠️  אין דומיין מוגדר, מנסה לקבל אוטומטית...")
        
        # נסה להשיג את הדומיין מהסביבה
        service_name = os.environ.get("RAILWAY_SERVICE_NAME", "bot")
        project_name = os.environ.get("RAILWAY_PROJECT_NAME", "")
        
        if project_name:
            domain = f"{project_name}-{service_name}.up.railway.app"
        else:
            domain = f"{service_name}.up.railway.app"
        
        print(f"🔗 דומיין משוער: {domain}")
        
        webhook_url = f"https://{domain}/{TELEGRAM_TOKEN}"
        
        try:
            app = Application.builder().token(TELEGRAM_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            
            app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_TOKEN,
                webhook_url=webhook_url,
                secret_token=TELEGRAM_TOKEN[:32],
                drop_pending_updates=True
            )
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            sys.exit(1)
    
    else:
        # מצב LOCAL עם polling
        print("💻 מצב LOCAL - משתמש ב-polling")
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            poll_interval=0.5
        )

if __name__ == "__main__":
    main()
