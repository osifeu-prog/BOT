# 📘 התקנת המערכת על Railway

ברוך הבא לשיעור ההתקנה. כאן נלמד איך להרים את הבוט, הקורס והמערכת כולה על Railway – צעד־אחר־צעד.

--- PAGE ---

## מה זה Railway ולמה להשתמש בו?

Railway היא פלטפורמה שמאפשרת לך:

- להעלות קוד (כמו הבוט שלך)
- לחבר מסד נתונים (Postgres)
- להגדיר משתני סביבה (Environment Variables)
- לקבל URL ציבורי (ל־Webhook)

במקום לנהל שרתים בעצמך – Railway עושה את זה עבורך.

--- PAGE ---

## יצירת פרויקט חדש ב-Railway

1. היכנס ל־https://railway.app
2. התחבר עם GitHub / Google.
3. לחץ על **New Project**.
4. בחר:
   - או "Deploy from GitHub" אם הקוד שלך ב-GitHub
   - או "Empty Project" ואז תעלה את הקוד ידנית.

המטרה: שתהיה לך סביבה שבה הקוד של הבוט רץ 24/7.

--- PAGE ---

## הוספת שירות (Service) לבוט

בפרויקט שלך:

1. לחץ על **New Service**.
2. אם אתה משתמש ב-GitHub:
   - בחר את הריפו שבו נמצא הקוד של הבוט.
3. אם אתה מעלה ידנית:
   - תוכל להשתמש ב־Railway CLI או ב־Deploy דרך ZIP.

לאחר ההעלאה, Railway ינסה להריץ את האפליקציה שלך.

--- PAGE ---

## משתני סביבה (Environment Variables)

עבור ל־**Variables** בפרויקט שלך והגדר:

- `TELEGRAM_TOKEN` – הטוקן שקיבלת מ־BotFather
- `WEBHOOK_URL` – ה-URL של ה־Webhook (לדוגמה: `https://your-app.up.railway.app/webhook`)
- `DATABASE_URL` – חיבור ל-Postgres (Railway יכול ליצור DB בשבילך)
- `REDIS_URL` – חיבור ל-Redis (לא חובה, אבל מומלץ)
- `DEBUG_MODE` – `true` כדי לראות לוגים חינוכיים

בנוסף, עבור המערכת המלאה:

- `PRICE_SH`, `LESSON_DB_PRICE`, `PEEK_COST`, `REFERRAL_REWARD`
- `CRYPTO_PAY_TOKEN`, `TON_WALLET`
- `PARTICIPANTS_GROUP_LINK`, `TEST_GROUP_LINK`

--- PAGE ---

## יצירת מסד נתונים (Postgres)

1. בפרויקט שלך ב-Railway, לחץ על **New** → **Database**.
2. בחר Postgres.
3. Railway ייצור עבורך `DATABASE_URL`.
4. העתק את ה־URL ל־Variables של שירות הבוט.

הקוד שלנו משתמש ב־`DATABASE_URL` כדי להתחבר למסד.

--- PAGE ---

## חיבור ה-Webhook ב-BotFather

1. פתח את BotFather בטלגרם.
2. שלח `/setwebhook`.
3. בחר את הבוט שלך.
4. הדבק את ה־`WEBHOOK_URL` שהגדרת ב-Railway.

אם הכול תקין – כשתשלח `/start` לבוט, הוא יענה.

--- PAGE ---

## בדיקת תקינות

בדוק:

1. האם `/` ב־Railway מחזיר JSON עם `"status": "Bot is running"`?
2. האם `/start` בטלגרם עובד?
3. האם אין שגיאות ב־Logs של Railway?

אם יש שגיאה – קרא את ה-Logs, חפש:
- ModuleNotFoundError
- ImportError
- שגיאות חיבור ל-DB

זה חלק מהלמידה – להבין איך לאבחן תקלות.
