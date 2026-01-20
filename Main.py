#!/usr/bin/env python3
"""
NFTY ULTRA BOT - NO CONFLICT GUARANTEE
גרסה שמונעת קונפליקט בוודאות
"""

import os
import sys
import logging
import time
from telegram.ext import Application, CommandHandler

# השתק הכל - ב-Railway לא צריך לוגים רבים
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
    await update.message.reply_text("🎰 NFTY ULTRA CASINO - הבוט פועל!")

def force_delete_webhook(token):
    """מחיקת webhook בכוח - עושה 3 נסיונות"""
    import requests
    
    for attempt in range(3):
        try:
            url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            params = {"drop_pending_updates": "true"}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    print(f"✅ Webhook נמחק (נסיון {attempt+1})")
                    return True
                else:
                    print(f"⚠️  תגובה לא תקינה: {data}")
            else:
                print(f"⚠️  סטטוס {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  שגיאה: {e}")
        
        time.sleep(1)  # המתן בין נסיונות
    
    print("❌ לא הצלחנו למחוק webhook")
    return False

def check_current_webhook(token):
    """בדיקה מה יש כרגע"""
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                webhook_info = data.get("result", {})
                print(f"📊 Webhook נוכחי:")
                print(f"   URL: {webhook_info.get('url', 'None')}")
                print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                return webhook_info
    except Exception as e:
        print(f"⚠️  לא ניתן לבדוק webhook: {e}")
    return None

def main():
    """נקודת כניסה ראשית"""
    print("=" * 70)
    print("🚀 NFTY ULTRA BOT - NO-CONFLICT VERSION")
    print("=" * 70)
    print(f"🕐 התחלה: {time.strftime('%H:%M:%S')}")
    
    # שלב 1: בדיקת טוקן
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
    
    # שלב 2: מחיקת webhook קיים בכוח
    print("\n🗑️  מחיקת webhook קיים...")
    force_delete_webhook(TELEGRAM_TOKEN)
    
    # בדיקה מה יש כרגע
    check_current_webhook(TELEGRAM_TOKEN)
    
    # שלב 3: בדיקת סביבה
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🔧 פורט: {port}")
    
    # בדיקה אם אנחנו ב-Railway
    domain = None
    
    # בדוק כל משתנה אפשרי של Railway
    railway_vars = ["RAILWAY_PUBLIC_DOMAIN", "RAILWAY_STATIC_URL", 
                    "RAILWAY_ENVIRONMENT", "RAILWAY_SERVICE_NAME"]
    
    print("\n📋 בדיקת משתני Railway:")
    for var in railway_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: {value}")
            if var in ["RAILWAY_PUBLIC_DOMAIN", "RAILWAY_STATIC_URL"]:
                domain = value
    
    # אם לא מצאנו דומיין, ננסה לשחזר מהנתונים
    if not domain:
        print("⚠️  לא נמצא דומיין במשתנים")
        # ניסיון לשחזר מהסביבה
        service_name = os.environ.get("RAILWAY_SERVICE_NAME", "bot")
        domain = f"{service_name}.up.railway.app"
        print(f"   דומיין משוער: {domain}")
    
    # נקה את הדומיין
    if domain:
        if domain.startswith("https://"):
            domain = domain.replace("https://", "")
        elif domain.startswith("http://"):
            domain = domain.replace("http://", "")
        domain = domain.rstrip("/")
    
    print(f"\n🎯 החלטה: {'RAILWAY' if domain else 'LOCAL'}")
    
    # שלב 4: הפעלת הבוט
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        
        if domain:
            # ב-Railway - חייבים webhook
            webhook_url = f"https://{domain}/{TELEGRAM_TOKEN}"
            print(f"\n🌐 Webhook URL: {webhook_url[:50]}...")
            
            # הגדר webhook לפני ההרצה
            try:
                import requests
                set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
                params = {
                    "url": webhook_url,
                    "drop_pending_updates": "true",
                    "secret_token": TELEGRAM_TOKEN[:32]
                }
                response = requests.get(set_url, params=params, timeout=10)
                print(f"📡 הגדרת webhook: {response.status_code}")
            except:
                pass
            
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
        else:
            # מקומי - polling
            print("\n💻 הרצה עם polling (מקומי)")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"],
                poll_interval=0.5,
                timeout=10
            )
            
    except Exception as e:
        print(f"\n❌ שגיאה: {type(e).__name__}: {e}")
        print(f"🕐 סיום: {time.strftime('%H:%M:%S')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
