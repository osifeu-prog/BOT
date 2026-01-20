import os
import sys
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# השתק לוגים מיותרים
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# הגדר logging רק לבוט שלנו
logging.basicConfig(
    format='%(asctime)s - NFTY ULTRA - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    """פקודת /start פשוטה"""
    await update.message.reply_text("🎰 NFTY ULTRA CASINO - הבוט פועל ומוכן!")

async def error_handler(update, context):
    """טיפול בשגיאות"""
    logger.error(f"Error: {context.error}")

def main():
    """נקודת כניסה ראשית"""
    print("=" * 60)
    print("🚀 NFTY ULTRA BOT - Railway Webhook Edition")
    print("=" * 60)
    
    # טען את הטוקן
    try:
        from config import TELEGRAM_TOKEN
    except ImportError:
        logger.error("❌ config.py לא נמצא או לא תקין")
        sys.exit(1)
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_TOKEN לא הוגדר!")
        print("⚠️ אנא הגדר את TELEGRAM_TOKEN ב-Railway Variables")
        sys.exit(1)
    
    print(f"✅ טוקן תקין: {TELEGRAM_TOKEN[:10]}...")
    
    try:
        # צור את האפליקציה
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # הוסף handlers
        app.add_handler(CommandHandler("start", start))
        app.add_error_handler(error_handler)
        
        # בדוק אם אנחנו ב-Railway (חייבים webhook)
        railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
        port = int(os.environ.get("PORT", 8080))
        
        if railway_domain:
            # מצב PRODUCTION - חייבים webhook ב-Railway
            print(f"🌐 PRODUCTION MODE - Railway")
            print(f"🔗 Domain: {railway_domain}")
            print(f"🔧 Port: {port}")
            
            webhook_url = f"https://{railway_domain}/{TELEGRAM_TOKEN}"
            print(f"🔗 Webhook URL: {webhook_url}")
            
            # מחיקת webhook קיים לפני הגדרת חדש
            try:
                import requests
                delete_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
                response = requests.get(f"{delete_url}?drop_pending_updates=true", timeout=5)
                if response.status_code == 200:
                    print("✅ Webhook קיים נמחק")
                else:
                    print(f"⚠️ לא ניתן למחוק webhook: {response.status_code}")
            except Exception as e:
                print(f"⚠️ שגיאה במחיקת webhook: {e}")
            
            # הפעל עם webhook
            app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_TOKEN,
                webhook_url=webhook_url,
                secret_token=TELEGRAM_TOKEN[:32],  # מונע התנגשויות
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
        else:
            # מצב DEVELOPMENT - polling
            print("💻 DEVELOPMENT MODE - Polling")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"],
                poll_interval=0.5
            )
            
    except Exception as e:
        print(f"❌ שגיאה: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
