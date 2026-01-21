📘 README.md — תיאור מלא של המערכת
markdown
# Telegram Modular Bot (FastAPI + Railway + PostgreSQL)

בוט טלגרם מודולרי, מהיר וקל לתחזוקה, המבוסס על FastAPI ורץ בענן Railway.  
המערכת בנויה כך שכל כפתור, כל הודעה וכל פעולה נמצאים בקובץ משלהם,  
ומאפשרת מעקב מלא אחרי כל אינטראקציה של המשתמש.

---

## 🚀 תכונות עיקריות

- **FastAPI Webhook** — שרת מהיר ויציב לקבלת עדכונים מטלגרם.
- **מבנה מודולרי מלא** — כל הודעה, כפתור ו־callback בקובץ משלו.
- **PostgreSQL Logging** — כל הודעה ולחיצה נשמרות בטבלה אחת.
- **גישה מוגבלת** — רק משתמשים מורשים (whitelist) יכולים להשתמש בבוט.
- **קל להרחבה** — הוספת כפתור/הודעה = יצירת קובץ חדש.
- **מוכן לפריסה בענן Railway**.

---

## 📁 מבנה הפרויקט

project/
│
├── main.py
├── requirements.txt
│
├── handlers/
│     ├── router.py
│     ├── callback_router.py
│     ├── start.py
│     └── echo.py
│
├── callbacks/
│     └── menu.py
│
├── buttons/
│     └── menus.py
│
├── texts/
│     └── messages.py
│
├── db/
│     ├── connection.py
│     └── events.py
│
└── utils/
├── telegram.py
└── config.py

קוד

---

## 🧠 לוגיקה בסיסית: כפתור = הודעה

המערכת בנויה על עיקרון פשוט:

1. משתמש לוחץ כפתור  
2. מגיע callback  
3. callback_router מפנה לפונקציה  
4. הפונקציה שולחת הודעה  
5. כל פעולה נרשמת ב־DB  

אין בלגן. אין קוד כפול. הכול ברור.

---

## 🗂️ קבצים מרכזיים

### `main.py`
שרת FastAPI שמקבל webhook מטלגרם.

### `handlers/router.py`
מטפל בכל הודעות הטקסט.

### `handlers/callback_router.py`
מטפל בכל לחיצות הכפתורים.

### `texts/messages.py`
כל ההודעות של הבוט במקום אחד.

### `buttons/menus.py`
כל הכפתורים במקום אחד.

### `db/events.py`
רישום כל פעולה של המשתמש (הודעה/כפתור).

---

## 🛢️ מבנה בסיס הנתונים

טבלה אחת שמכסה הכול:

```sql
user_events (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    event_type VARCHAR(50),   -- message / button / command
    event_key TEXT,
    payload TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)
🔐 הרשאות
רק משתמשים שמופיעים ב־ALLOWED_USERS בקובץ:

קוד
utils/config.py
יכולים להשתמש בבוט.

☁️ פריסה בענן Railway
1. חיבור ל־GitHub
Create New Project → Deploy from GitHub

2. בחירת branch
Settings → GitHub → Branch → master

3. משתני סביבה
Settings → Variables:

קוד
TELEGRAM_TOKEN = <your token>
DATABASE_URL = <postgres url>
4. פקודת הרצה
Settings → Deploy → Start Command:

קוד
uvicorn main:app --host 0.0.0.0 --port 8000
5. Redeploy
Deployments → Redeploy

🤖 הגדרת Webhook בטלגרם
לאחר הפריסה, קבל את ה־URL של Railway:

קוד
https://your-app.up.railway.app
הגדר Webhook:

קוד
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-app.up.railway.app/webhook
🧪 בדיקה
בטלגרם:

קוד
/start
אמור להופיע:

הודעת ברוך הבא

תפריט כפתורים

כל לחיצה תירשם ב־DB

🧩 הרחבת המערכת
הוספת כפתור חדש
הוסף כפתור ב־buttons/menus.py

צור פונקציה חדשה ב־callbacks/

הוסף תנאי ב־callback_router.py

הוספת הודעה חדשה
הוסף טקסט ב־texts/messages.py

צור handler חדש ב־handlers/

הוסף תנאי ב־router.py

🟦 סיכום
המערכת הזו נותנת:

שליטה מלאה

מבנה נקי

קוד מודולרי

מעקב אחרי כל פעולה

פריסה בענן

בסיס מושלם להתרחבות

בדיוק כמו שרצית —
כפתור = הודעה = קובץ = שליטה מלאה.

קוד

---
.
