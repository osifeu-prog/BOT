# 📂 כל הקוד מוסבר – מדריך מלא

בשיעור הזה נעבור על כל הקבצים המרכזיים במערכת, ונסביר מה כל חלק עושה.

--- PAGE ---

## main.py

- יוצר FastAPI
- מגדיר:
  - `GET /` – בדיקת חיים
  - `POST /webhook` – נקודת כניסה לעדכונים מטלגרם
- קורא ל:
  - `handle_message` עבור `message`
  - `handle_callback` עבור `callback_query`

זה השער הראשי בין טלגרם לקוד שלך.

--- PAGE ---

## utils/config.py

- קורא משתני סביבה:
  - טוקן הבוט
  - URL של ה-Webhook
  - חיבור ל-DB
  - חיבור ל-Redis
  - מחירים
  - פרטי תשלום
- מגדיר פרטי קשר שלך (טלפון, מייל, טלגרם)

כך אפשר לשנות הגדרות בלי לגעת בקוד.

--- PAGE ---

## utils/telegram.py

- `send_message` – שולח הודעת טקסט
- `send_document` – שולח קובץ (או לינק לקובץ)

עטיפה פשוטה ל-Telegram Bot API, כדי שלא תצטרך לכתוב `requests.post` בכל מקום.

--- PAGE ---

## utils/i18n.py

- `detect_language_from_telegram` – מחזיר `he` או `en`
- `t(lang, he, en)` – בוחר טקסט לפי שפה

כך אפשר לכתוב טקסטים דו־לשוניים בצורה נקייה.

--- PAGE ---

## utils/edu_log.py

- `edu_step` – מדפיס שלב ממוספר
- `edu_path` – מדפיס נתיב זרימה
- `edu_warning` / `edu_error` – מדפיסים אזהרות ושגיאות

כש־`DEBUG_MODE=true`, תראה את כל זה ב־Logs.

--- PAGE ---

## db/connection.py

- יוצר חיבור ל-Postgres לפי `DATABASE_URL`.

שאר קבצי ה־DB משתמשים בו כדי לא לפתוח חיבורים בצורה כפולה.

--- PAGE ---

## db/admins.py, db/buyers.py

- `admins.py` – מי אדמין
- `buyers.py` – מי רכש

פונקציות:

- `_ensure_table` – יוצרת טבלה אם לא קיימת
- `is_admin` / `is_buyer`
- `add_admin` / `add_buyer`

--- PAGE ---

## db/events.py

- טבלת `user_events`:
  - `user_id`
  - `event_type`
  - `data`
  - `created_at`

פונקציה:

- `log_event` – רושמת אירוע חדש.

--- PAGE ---

## db/slots.py, db/stats.py, db/course_progress.py

- `slots.py` – היסטוריית משחק SLOTS
- `stats.py` – סטטיסטיקות בסיסיות (משתמשים, רוכשים, אירועים)
- `course_progress.py` – התקדמות בקורס (Redis)

כל אחד מהם אחראי על טבלה / תחום מסוים.

--- PAGE ---

## handlers/router.py

- מקבל הודעות טקסט.
- מזהה:
  - `/start`
  - `/admin`
- שולח תפריט ראשי או מעביר ל־`admin_handler`.

--- PAGE ---

## handlers/callback_router.py

- מקבל `callback_query`.
- אם `data` מתחיל ב־`menu_` – מעביר ל־`menu_callback`.
- אם `data` מתחיל ב־`course|` – מעביר ל־`course_callback`.

--- PAGE ---

## handlers/admin.py

- `/admin <password>` – הופך משתמש לאדמין.
- `/grant <user_id>` – נותן גישה לקורס.
- `/astats` – סטטיסטיקות.
- `/alogs` – אירועים אחרונים.
- `/export buyers` / `/export events` – יצוא CSV (לוגיקה בסיסית).

--- PAGE ---

## handlers/slots.py

- `play_slots` – מריץ משחק אחד.
- `show_leaderboard` – מציג טבלת מובילים.

משתמש ב־`WIN_CHANCE_PERCENT` כדי לשלוט בסיכוי לזכייה.

--- PAGE ---

## callbacks/menu.py

- מטפל בכל כפתורי `menu_*`.
- כולל:
  - רכישה
  - קורס
  - איך הבוט עובד
  - ממשק טלגרם
  - משחק
  - טבלת מובילים
  - תמיכה

--- PAGE ---

## callbacks/course.py

- `LESSON_FILES` – מיפוי שיעורים לקבצי Markdown.
- `send_lesson_page` – מציג עמוד מסוים:
  - מצב דמו
  - בדיקת רוכש / אדמין
  - שמירת התקדמות
- `course_callback` – מפענח `course|LESSON_KEY|PAGE_INDEX`.

--- PAGE ---

## buttons/menus.py

- `get_main_menu` – תפריט ראשי.
- `get_course_menu` – תפריט שיעורי הקורס.

כל כפתור מכיל `callback_data` שמתחבר ללוגיקה.

--- PAGE ---

## texts/*.py

- `payment.py` – טקסטי תשלום.
- `how_it_works.py` – תקציר על איך הבוט עובד.
- `telegram_ui.py` – תקציר על ממשק טלגרם.

טקסטים דו־לשוניים לשימוש מהיר.

--- PAGE ---

## course/*.md

- כל שיעור בקורס.
- מחולק לעמודים עם `--- PAGE ---`.
- כולל:
  - הסברים
  - דוגמאות
  - משימות

הבוט מציג אותם לפי לחיצות המשתמש.

--- PAGE ---

## landing/

- `index.html` – דף נחיתה.
- `style.css` – עיצוב.

אפשר להרחיב, להוסיף טפסים, וידאו, עדויות ועוד.

--- PAGE ---

## סיכום

עכשיו יש לך:

- קוד מלא
- קורס מלא
- הסברים לכל חלק
- תבנית להקמת בוטים ומוצרים נוספים

מכאן – זה כבר שלך: לשחק, לשנות, למכור, ללמד.
