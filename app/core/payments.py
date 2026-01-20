import httpx
import json
from config import CRYPTO_PAY_TOKEN

async def create_payment(user_id, amount_usd, tier_name):
    """
    Create a payment invoice via CryptoBot
    """
    if not CRYPTO_PAY_TOKEN:
        return {"ok": False, "error": "CryptoBot token not configured"}
    
    # Convert USD to USDT (1:1 for simplicity)
    amount = float(amount_usd)
    
    # Create invoice
    payload = {
        "asset": "USDT",
        "amount": str(amount),
        "description": f"Upgrade to {tier_name} Tier",
        "hidden_message": f"Thank you for upgrading to {tier_name}!",
        "paid_btn_name": "open_bot",
        "paid_btn_url": f"https://t.me/{BOT_USERNAME.replace('@', '')}",
        "payload": f"{user_id}:{tier_name}",
        "allow_comments": False
    }
    
    headers = {
        "Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://pay.crypt.bot/api/createInvoice",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return {
                        "ok": True,
                        "result": {
                            "invoice_id": data["result"]["invoice_id"],
                            "pay_url": data["result"]["pay_url"],
                            "amount": data["result"]["amount"]
                        }
                    }
                else:
                    return {"ok": False, "error": data.get("error", "Unknown error")}
            else:
                return {"ok": False, "error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        return {"ok": False, "error": str(e)}
