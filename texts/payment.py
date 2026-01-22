"""
payment.py
==========
HE: טקסטים הקשורים לתשלום ורכישה.
EN: Payment-related texts.
"""

from utils.config import SUPPORT_CONTACT_TEXT_HE, SUPPORT_CONTACT_TEXT_EN, PRICE_SH, TON_WALLET
from utils.i18n import LanguageCode, t

def get_payment_message(lang: LanguageCode) -> str:
    """
    HE: מחזיר הודעת תשלום לפי שפה.
    EN: Returns payment message by language.
    """
    price_str = f"{PRICE_SH:.0f}"
    return t(
        lang,
        he=(
            f"כדי לקבל את ערכת הסטארטאפ המלאה (בוט + קורס + קוד + דף נחיתה):\n\n"
            f"💰 עלות: {price_str} ש\"ח\n"
            f"💎 תשלום ב-TON:\n"
            f"{TON_WALLET}\n\n"
            f"לאחר התשלום, שלח צילום מסך של ההעברה.\n"
            f"לאחר אישור — תקבל גישה מלאה לקורס, לקוד ול־ZIP.\n\n"
            f"ליצירת קשר בכל שלב:\n{SUPPORT_CONTACT_TEXT_HE}"
        ),
        en=(
            f"To get the full startup kit (bot + course + code + landing page):\n\n"
            f"💰 Price: {price_str} ILS (approx.)\n"
            f"💎 Pay with TON:\n"
            f"{TON_WALLET}\n\n"
            f"After payment, send a screenshot of the transfer.\n"
            f"Once approved — you'll get full access to the course, code and ZIP.\n\n"
            f"For support at any stage:\n{SUPPORT_CONTACT_TEXT_EN}"
        )
    )
