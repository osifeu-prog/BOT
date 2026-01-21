"""
texts/payment.py
=================
מכיל את הודעת התשלום למשתמש.
"""

from utils.config import SUPPORT_CONTACT_TEXT

def get_payment_message():
    return (
        "כדי לקבל את קובץ ה־ZIP של הפרויקט והקורס המלא:\n\n"
        "💰 עלות: 254 ש\"ח\n"
        "💎 תשלום דרך TON:\n"
        "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp\n\n"
        "לאחר התשלום, שלח צילום מסך של ההעברה.\n"
        "לאחר אישור — תקבל גישה מלאה לקורס ולכל הקבצים.\n\n"
        "ליצירת קשר בכל שלב:\n"
        f"{SUPPORT_CONTACT_TEXT}"
    )
