def get_welcome_text(lang: str, name: str) -> str:
    if lang.startswith("he"):
        return f"""
🎉 ברוך הבא לבוט הרשמי של *Osif Shop*, {name}!

כאן תוכל לרכוש את הפרויקט המלא:

✔️ קוד מקור מלא
✔️ מערכת מנהלים מובנית
✔️ תיעוד מלא + מדריך התקנה
✔️ תמיכה מלאה בהעלאה ל־Railway
✔️ מערכת תשלומים + שליחת ZIP אוטומטית
✔️ משחק SLOTS עם ניקוד וטבלת מובילים

בחר אחת מהאפשרויות למטה כדי להתחיל 👇
"""
    else:
        return f"""
🎉 Welcome to the official *Osif Shop* bot, {name}!

Here you can purchase the full project:

✔️ Full source code
✔️ Built-in admin system
✔️ Full documentation + install guide
✔️ Railway deployment support
✔️ Payment flow + automatic ZIP delivery
✔️ SLOTS game with points and leaderboard

Choose an option below to get started 👇
"""
