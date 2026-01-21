# 📘 התקנת המערכת על Railway

ברוך הבא לשיעור ההתקנה. כאן נלמד איך להרים את הבוט, הקורס והמערכת כולה על Railway.

--- PAGE ---

## שלב 1: יצירת פרויקט ב-Railway

1. היכנס ל־https://railway.app
2. צור פרויקט חדש.
3. הוסף שירות חדש (New Service) → Deploy from GitHub או Manual Deploy.

---

## שלב 2: משתני סביבה (Environment Variables)

בפרויקט שלך ב-Railway, עבור ל־**Variables** והגדר:

- `TELEGRAM_TOKEN` — הטוקן שקיבלת מ־BotFather
- `WEBHOOK_URL` — ה-URL של ה־Webhook (לדוגמה: https://your-app.up.railway.app/webhook)
- `DATABASE_URL` — חיבור ל-Postgres (Railway יכול ליצור DB בשבילך)
- `REDIS_URL` — חיבור ל-Redis (אופציונלי אבל מומלץ)
- `DEBUG_MODE` — `true` כדי לראות לוגים חינוכיים

--- PAGE ---

## שלב 3: חיבור ה-Webhook ב-BotFather

1. פתח את BotFather בטלגרם.
2. שלח `/setwebhook`.
3. בחר את הבוט שלך.
4. הדבק את ה־`WEBHOOK_URL` שהגדרת ב-Railway.

אם הכול תקין — כשתשלח `/start` לבוט, הוא יענה.

--- PAGE ---

## סיכום

בשלב זה:

- יש לך פרויקט ב-Railway
- הבוט מחובר ל-Webhook
- משתני הסביבה מוגדרים
- אתה מוכן להמשיך לשיעור הבא: איך הבוט עובד מבפנים.
