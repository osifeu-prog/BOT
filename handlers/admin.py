from utils.telegram import send_message, send_document
from db.admins import add_admin, is_admin
from db.buyers import add_buyer
from db.stats import get_basic_stats, get_recent_events
from db.connection import get_conn
from utils.i18n import LanguageCode, t
from utils.config import ADMIN_PASSWORD
from utils.edu_log import edu_step, edu_path

import csv
import io

async def admin_handler(message: dict, lang: LanguageCode):
    user_id = message["from"]["id"]
    text = message.get("text", "") or ""

    edu_path("USER → ADMIN_HANDLER")
    edu_step(1, f"Admin handler invoked by user {user_id} with text: {text!r}")

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

    if not is_admin(user_id):
        return send_message(
            user_id,
            t(lang, "אין לך הרשאות אדמין.", "You don't have admin permissions.")
        )

    # /grant <user_id>
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

    # /astats – סטטיסטיקות בסיסיות
    if text.startswith("/astats"):
        stats = get_basic_stats()
        msg = t(
            lang,
            he=(
                "📊 סטטיסטיקות מערכת:\n"
                f"משתמשים ייחודיים: {stats['total_users']}\n"
                f"רוכשים: {stats['total_buyers']}\n"
                f"סה\"כ אירועים: {stats['total_events']}\n"
                f"משחקי SLOTS: {stats['total_slots_games']}\n"
            ),
            en=(
                "📊 System stats:\n"
                f"Unique users: {stats['total_users']}\n"
                f"Buyers: {stats['total_buyers']}\n"
                f"Total events: {stats['total_events']}\n"
                f"SLOTS games: {stats['total_slots_games']}\n"
            )
        )
        return send_message(user_id, msg)

    # /alogs – אירועים אחרונים
    if text.startswith("/alogs"):
        rows = get_recent_events()
        if not rows:
            return send_message(
                user_id,
                t(lang, "אין אירועים.", "No events.")
            )
        lines = []
        for uid, etype, data, created_at in rows:
            lines.append(f"{created_at} | {uid} | {etype} | {data or ''}")
        msg = "\n".join(lines)
        return send_message(
            user_id,
            t(lang, "🧾 אירועים אחרונים:\n", "🧾 Recent events:\n") + msg
        )

    # /export buyers | events
    if text.startswith("/export"):
        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            return send_message(
                user_id,
                t(lang, "שימוש: /export buyers|events", "Usage: /export buyers|events")
            )
        what = parts[1].strip()
        if what == "buyers":
            return _export_buyers_csv(user_id, lang)
        elif what == "events":
            return _export_events_csv(user_id, lang)
        else:
            return send_message(
                user_id,
                t(lang, "אפשרויות: buyers או events", "Options: buyers or events")
            )

    # תפריט עזרה לאדמין
    help_text = t(
        lang,
        he=(
            "פקודות אדמין זמינות:\n"
            "/grant <user_id> – לתת גישה לקורס\n"
            "/astats – סטטיסטיקות מערכת\n"
            "/alogs – אירועים אחרונים\n"
            "/export buyers – יצוא רוכשים ל-CSV\n"
            "/export events – יצוא אירועים ל-CSV\n"
        ),
        en=(
            "Available admin commands:\n"
            "/grant <user_id> – grant course access\n"
            "/astats – system stats\n"
            "/alogs – recent events\n"
            "/export buyers – export buyers to CSV\n"
            "/export events – export events to CSV\n"
        )
    )
    return send_message(user_id, help_text)


def _export_buyers_csv(admin_id: int, lang: LanguageCode):
    edu_path("ADMIN → EXPORT_BUYERS_CSV")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, created_at FROM buyers ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "created_at"])
    for uid, created_at in rows:
        writer.writerow([uid, created_at])

    output.seek(0)
    csv_data = output.read()

    # שולחים כקובץ "buyers.csv" דרך sendDocument
    send_document(
        admin_id,
        file_url=f"attach://buyers.csv",  # בטלגרם אמיתי צריך multipart, כאן זה דמו לוגי
        caption=t(lang, "קובץ רוכשים (CSV).", "Buyers CSV file.")
    )
    # בפועל, אם תרצה ממש Multipart – תעדכן את wrapper של send_document.


def _export_events_csv(admin_id: int, lang: LanguageCode):
    edu_path("ADMIN → EXPORT_EVENTS_CSV")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, event_type, data, created_at
        FROM user_events
        ORDER BY created_at DESC
        LIMIT 1000
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "event_type", "data", "created_at"])
    for uid, etype, data, created_at in rows:
        writer.writerow([uid, etype, data or "", created_at])

    output.seek(0)
    csv_data = output.read()

    send_document(
        admin_id,
        file_url=f"attach://events.csv",
        caption=t(lang, "קובץ אירועים (CSV).", "Events CSV file.")
    )
