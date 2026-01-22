import requests
from utils.config import CRYPTO_PAY_TOKEN

def create_invoice(amount_usd: float):
    """יוצר בקשת תשלום ב-CryptoBot"""
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    payload = {
        "asset": "USDT",
        "amount": str(amount_usd),
        "description": "Purchase Startup Bot Kit",
        "paid_btn_name": "callback",
        "paid_btn_url": "https://t.me/YourBot"
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json().get("result", {}).get("pay_url")

def check_payment(invoice_id: str):
    """בודק אם החשבונית שולמה"""
    url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    resp = requests.get(url, headers=headers)
    invoices = resp.json().get("result", {}).get("items", [])
    if invoices and invoices[0]['status'] == 'paid':
        return True
    return False
