# 🎰 Telegram Casino Bot - Railway Edition

בוט קזינו מתקדם הכולל מערכת CRM, ניהול נקודות ואנימציות מובנות.

## 🚀 הגדרות מהירות ב-Railway
1. וודא שכל המשתנים (Variables) מוגדרים (TELEGRAM_TOKEN, DATABASE_URL וכו').
2. הבוט משתמש ב-**Postgres** לשמירת יתרות משתמשים.
3. הבוט משתמש ב-**Dice API** של טלגרם לחווית משחק ויזואלית.

## 🛠 פקודות אדמין
- גישה ללוח הבקרה ניתנת רק ל-`ADMIN_ID`.
- ניתן לשנות את ה-`WIN_CHANCE_PERCENT` מהגדרות המערכת בזמן אמת.

## 📈 מודל כלכלי
- המשתמשים מקבלים נקודות התחלתיות.
- ניתן להוסיף כפתור תשלום דרך `CRYPTO_PAY_TOKEN` לטעינת נקודות.
