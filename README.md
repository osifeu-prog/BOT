# 🎰 Advanced Casino Bot - CRM & Economy

מערכת קזינו מבוססת טלגרם עם ניהול משתמשים מלא.

## ✨ תכונות עיקריות
- **CRM מובנה:** מעקב אחרי יתרות, הפקדות ותאריכי הצטרפות ב-Postgres.
- **מערכת Referrals:** לינקים ייחודיים לכל משתמש עם תגמול אוטומטי.
- **אנימציות:** שימוש ב-Dice API של טלגרם לחוויה מקסימלית.
- **Admin Panel:** שליטה בסיכויי הזכייה ובמשתמשים ישירות מהבוט.

## 🛠 הגדרת המשתנים ב-Railway
| Variable | Description |
|----------|-------------|
| `TELEGRAM_TOKEN` | הטוקן מ-BotFather |
| `DATABASE_URL` | חיבור ה-Postgres |
| `ADMIN_ID` | ה-ID שלך בטלגרם |
| `WIN_CHANCE_PERCENT` | סיכוי זכייה (למשל 25) |
| `WEBHOOK_URL` | הכתובת של ה-Service ברלוויי |

## 🚀 התקנה
1. דחוף את כל הקבצים ל-GitHub.
2. חבר את ה-Repo ל-Railway.
3. וודא שפורט 8080 פתוח ב-Settings.
