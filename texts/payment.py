"""
texts/payment.py
=================
מכיל את הודעת התשלום למשתמש.
"""

from utils.config import PRICE_SH, TON_WALLET

def get_payment_message():
    return f"""
כדי לקבל את קובץ ה־ZIP של הפרויקט:

💰 עלות: {PRICE_SH} ש"ח  
💎 תשלום דרך TON:  
`{TON_WALLET}`

לאחר התשלום, שלח צילום מסך של ההעברה.
לאחר אישור — תקבל את הקובץ אוטומטית.
"""
