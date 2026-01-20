#!/usr/bin/env python3
"""
בדיקת webhook נוכחי
"""

import requests
import os
from config import TELEGRAM_TOKEN

def check_webhook():
    """בדוק מהו ה-webhook הנוכחי"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        print("🔍 בדיקת Webhook נוכחי:")
        print(f"✅ OK: {data.get('ok')}")
        
        if data.get('ok'):
            result = data.get('result', {})
            print(f"📡 URL: {result.get('url', 'None')}")
            print(f"📦 Pending updates: {result.get('pending_update_count', 0)}")
            print(f"🤖 יכול לקלוט updates: {result.get('has_custom_certificate', False)}")
            
            # אם יש URL, נמחק אותו
            if result.get('url'):
                print("\n🗑️  מוחק webhook קיים...")
                delete_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
                del_response = requests.get(delete_url, params={"drop_pending_updates": "true"})
                print(f"✅ {del_response.json().get('description', 'נמחק')}")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == "__main__":
    check_webhook()
