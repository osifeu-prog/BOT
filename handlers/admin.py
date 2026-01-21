"""
handlers/admin.py
==================
טיפול בפקודות אדמין, כולל:
- הוספת אדמין
- הוספת רוכש (buyer)
"""
from utils.telegram import send_message
from db.admins import add_admin, is_admin
from db.buyers import add_buyer

ADMIN_PASSWORD = "NFTY2026"

async def admin_handler(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")

    if text.startswith("/admin"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2 and parts[1].strip() == ADMIN_PASSWORD:
            add_admin(user_id)
            return send_message(user_id, "✅ אתה עכשיו אדמין.")
        else:
            return send_message(user_id, "❌ סיסמה שגויה.")

    if not is_admin(user_id):
        return send_message(user_id, "אין לך הרשאות אדמין.")

    if text.startswith("/grant"):
        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            return send_message(user_id, "שימוש: /grant <user_id>")
        try:
            target_id = int(parts[1].strip())
        except ValueError:
            return send_message(user_id, "user_id לא תקין.")
        add_buyer(target_id)
        return send_message(user_id, f"✅ המשתמש {target_id} קיבל גישה לקורס.")

    return send_message(user_id, "פקודת אדמין לא מוכרת.")
