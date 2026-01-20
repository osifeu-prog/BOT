import os
from CryptoPayAPI.CryptoPay import CryptoPay
from CryptoPayAPI.types.asset import USDT  # אפשר להחליף ל‑TON אם תרצה

CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")

cryptopay = CryptoPay(token=CRYPTO_PAY_TOKEN)

def create_lesson_invoice(amount):
    """
    יוצר חשבונית תשלום לשיעור, ומחזיר URL לתשלום.
    """
    try:
        invoice = cryptopay.create_invoice(
            amount=amount,
            asset=USDT  # אפשר להחליף ל‑TON אם תרצה
        )
        return invoice.bot_invoice_url
    except Exception as e:
        print("CryptoPay error:", e)
        return None
