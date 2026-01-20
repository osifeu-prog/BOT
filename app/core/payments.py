import httpx, os
from config import TELEGRAM_TOKEN
from app.database.manager import db

CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN") # תקבל אותו מ-@CryptoBot
API_URL = "https://pay.crypt.bot/api/createInvoice"

async def create_payment(uid, amount, tier_name):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    payload = {
        "asset": "USDT",
        "amount": str(amount),
        "description": f"Upgrade to {tier_name} Tier",
        "payload": f"{uid}:{tier_name}", # שומרים את ה-ID והדרגה בתוך החשבונית
        "paid_btn_name": "callback",
        "paid_btn_url": f"https://t.me/YOUR_BOT_NAME"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(API_URL, json=payload, headers=headers)
        return r.json()
