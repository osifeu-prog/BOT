import httpx, json, os
from fastapi import FastAPI, Request
from app.database.manager import db

app = FastAPI()

@app.post("/webhook/cryptobot")
async def handle_crypto_webhook(request: Request):
    data = await request.json()
    
    if data.get("status") == "paid":
        # פרטי התשלום
        invoice_id = data.get("invoice_id")
        payload = data.get("payload", "").split(":")
        
        if len(payload) == 2:
            user_id, tier_name = payload
            amount = float(data.get("amount", 0))
            
            # עדכון משתמש
            db.set_tier(int(user_id), tier_name)
            db.log_transaction(int(user_id), amount, f"Upgrade to {tier_name}")
            
            # שליחת הודעה למשתמש
            # (ניתן לשלוח כאן הודעה דרך הבוט)
    
    return {"status": "ok"}

# פונקציה ליצירת לינק תשלום מלא
async def create_payment_link(user_id, amount_usd, tier_name):
    crypto_data = await create_payment(user_id, amount_usd, tier_name)
    
    if crypto_data.get("ok"):
        payment_url = crypto_data["result"]["pay_url"]
        return f"""
💳 **תשלום עבור {tier_name} Tier**

💰 סכום: ${amount_usd}
🎯 חבילה: {tier_name}
👤 מזהה: {user_id}

🔗 [לחץ כאן לתשלום]({payment_url})

⚡ התשלום מאובטח דרך CryptoBot
✅ אחרי התשלום - הדרגה תשתנה אוטומטית!
        """
    return None
