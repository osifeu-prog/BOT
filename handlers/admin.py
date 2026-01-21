"""
admin.py
========
HE: לוגיקת אדמין — הפיכת משתמש לאדמין, מתן גישה לקורס וכו'.
EN: Admin logic — making a user admin, granting course access, etc.
"""

from utils.telegram import send_message
from db.admins import add_admin, is_admin
from db.buyers import add_buyer
from utils.i18n import LanguageCode, t
from utils.config import ADMIN_PASSWORD
from utils.edu_log import edu_step, edu_path

async def admin_handler(message: dict, lang: LanguageCode):
    """
    HE: מטפל בפקודות אדמין.
    EN: Handles admin commands.
    """
    user_id = message["from"]["id"]
    text = message.get("text", "") or ""

    edu_path("USER → ADMIN_HANDLER")
    edu_step(1, f"Admin handler invoked by user {user_id} with text: {text!r}")

    # HE: /admin <password> — הפיכת המשתמש לאדמין
    # EN: /admin <password> — make the user an admin
    if text.startswith("/admin"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2 and parts[1].strip() == ADMIN_PASSWORD:
            add_admin(user_id)
            return send_message(
                user_id,
                t(lang, "✅ אתה עכשיו אדמין.", "✅ You are now an admin.")
            )
        else:
            return send_message(
                user_id,
                t(lang, "❌ סיסמה שגויה.", "❌ Wrong password.")
            )

    # HE: אם המשתמש לא אדמין — אין גישה
    # EN: If the user is not an admin — no access
    if not is_admin(user_id):
        return send_message(
            user_id,
            t(lang, "אין לך הרשאות אדמין.", "You don't have admin permissions.")
        )

    # HE: /grant <user_id> — נותן גישה לקורס למשתמש אחר
    # EN: /grant <user_id> — grants course access to another user
    if text.startswith("/grant"):
        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            return send_message(
                user_id,
                t(lang, "שימוש: /grant <user_id>", "Usage: /grant <user_id>")
            )
        try:
            target_id = int(parts[1].strip())
        except ValueError:
            return send_message(
                user_id,
                t(lang, "user_id לא תקין.", "Invalid user_id.")
            )
        add_buyer(target_id)
        return send_message(
            user_id,
            t(lang, f"✅ המשתמש {target_id} קיבל גישה לקורס.", f"✅ User {target_id} has been granted access.")
        )

    return send_message(
        user_id,
        t(lang, "פקודת אדמין לא מוכרת.", "Unknown admin command.")
    )
