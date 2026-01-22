# Osif Telegram Shop Bot

בוט טלגרם מודולרי למכירת פרויקטים דיגיטליים (כמו קבצי ZIP),  
מבוסס FastAPI, PostgreSQL ו־Railway, עם מערכת מנהלים, תשלומים, ותיעוד מלא.

## מה הבוט יודע לעשות?

- להציג תפריט רכישה ברור
- לקבל תשלום דרך TON (ידני, עם צילום מסך)
- לאפשר למשתמשים להפוך למנהלים עם סיסמה
- לשלוח קובץ ZIP לאחר אישור תשלום
- לתעד כל פעולה במסד נתונים
- לאפשר לך להרחיב, למתג ולמכור את הבוט הלאה

## למי זה מיועד?

- למי שרוצה למכור קבצים / קורסים / פרויקטים דרך טלגרם
- למי שרוצה בוט נקי, מודולרי, קל לתחזוקה
- למי שרוצה מוצר שאפשר למכור הלאה ללקוחות

## מה הלאה?

- קרא את `INSTALL.md` כדי להרים את הבוט אצלך
- קרא את `HOW_IT_WORKS.md` כדי להבין את הזרימה
- קרא את `ARCHITECTURE.md` כדי להבין את המבנה
docs/INSTALL.md
markdown
# התקנה והפעלה

## דרישות

- חשבון Telegram Bot (דרך BotFather)
- חשבון Railway
- PostgreSQL (דרך Railway)
- Python 3.10+

## שלב 1 — שכפול הפרויקט

git clone <repo-url>
cd project
pip install -r requirements.txt
שלב 2 — הגדרת משתני סביבה ב־Railway
ב־Railway → Variables:

env
TELEGRAM_TOKEN=
ADMIN_ID=
ADMIN_PASSWORD=
PRICE_SH=
TON_WALLET=
ZIP_LINK=https://your-zip-link
DATABASE_URL=
שלב 3 — פריסה ב־Railway
חבר את הריפו ל־Railway

ב־Start Command:

bash
uvicorn main:app --host 0.0.0.0 --port $PORT
Redeploy

שלב 4 — הגדרת Webhook
text
https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://<your-app>.up.railway.app/webhook
שלב 5 — בדיקה
בטלגרם:

text
/start
אם אתה רואה:

תמונה

תפריט

כפתור "רכישת הפרויקט"

הכול עובד.

קוד

---

#### `docs/ARCHITECTURE.md`

```markdown
# ארכיטקטורת המערכת

## שכבות

1. Telegram → Webhook → FastAPI (`main.py`)
2. Router להודעות (`handlers/router.py`)
3. Router לכפתורים (`handlers/callback_router.py`)
4. Handlers (start, admin, echo, send_zip)
5. DB (events, admins)
6. Utils (config, telegram, photos)
7. Texts (messages, payment, how_it_works)

## תרשים זרימה — הודעות

```text
Telegram → /webhook → main.py
    └── message → handlers/router.py
            ├── /admin → handlers/admin.py → db/admins.py
            ├── "אושר" → handlers/send_zip.py
            ├── /start → handlers/start.py
            └── אחר → handlers/echo.py
תרשים זרימה — כפתורים
text
Telegram → /webhook → main.py
    └── callback_query → handlers/callback_router.py
            └── menu_* → callbacks/menu.py
                    ├── menu_buy → texts/payment.py
                    └── menu_help → הודעת עזרה
תיעוד ב־DB
text
כל פעולה → db/events.py → user_events
כל מנהל → db/admins.py → admins
קוד

---

#### `docs/HOW_IT_WORKS.md`

פשוט העתק את התוכן של `HOW_IT_WORKS` מ־`texts/how_it_works.py` (אותו טקסט).

---

#### `docs/FAQ.md`

```markdown
# FAQ — שאלות נפוצות

## הבוט לא מגיב ל־/start

- בדוק שה־Webhook מוגדר נכון
- בדוק ש־TELEGRAM_TOKEN נכון
- בדוק שהשרת ב־Railway רץ
- בדוק לוגים ב־Railway

## איך מוסיפים מנהל חדש?

1. תן לו לשלוח:

```text
/admin <ADMIN_PASSWORD>
הוא ייכנס לטבלת admins.

איך משנים מחיר?
שנה את PRICE_SH ב־Railway Variables.

איך מחליפים ZIP?
שנה את ZIP_LINK ב־Railway Variables.

קוד

---

#### `docs/UI_UX_TIPS.md`

```markdown
# טיפים ל־UI/UX

- שמור על טקסטים קצרים וברורים
- אל תעמיס יותר מדי כפתורים
- השתמש באימוג'ים במידה
- תן תמיד פידבק אחרי פעולה (למשל: "קיבלתי", "אושר", "נשלח")
- ודא שתמיד יש דרך "לחזור להתחלה" (/start)



3. תרשים זרימה נוסף — תיעוד כל פעולה
text
משתמש שולח הודעה
    ↓
Telegram → /webhook → main.py
    ↓
handlers/router.py
    ↓
db/events.log_event(...)
    ↓
טבלת user_events

משתמש הופך למנהל
    ↓
/admin <password>
    ↓
handlers/admin.py
    ↓
db/admins.add_admin(...)
    ↓
טבלת admins
