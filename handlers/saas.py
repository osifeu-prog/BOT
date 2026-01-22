from utils.config import BASE_URL, SUPPORT_EMAIL, SUPPORT_PHONE, WHATSAPP_LINK

def get_support_info():
    return (f"📩 **צור קשר עם ההנהלה**\n\n"
            f"🌐 אתר רשמי: {BASE_URL}\n"
            f"📧 מייל: {SUPPORT_EMAIL}\n"
            f"📱 טלפון: {SUPPORT_PHONE}\n\n"
            f"💬 לשליחת וואטסאפ מהירה: [לחץ כאן]({WHATSAPP_LINK})")

def get_marketplace():
    return ("🛒 **חנות הבוטים והשירותים**\n\n"
            "1️⃣ **בוט ניהול קבוצות PRO** - 500 SLH\n"
            "2️⃣ **בוט מסחר אוטומטי (Beta)** - 1500 SLH\n"
            "3️⃣ **שירות סוכן AI אישי** - 200 SLH/חודש\n\n"
            "לרכישה, פנה לתמיכה הטכנית.")
