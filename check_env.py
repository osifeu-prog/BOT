import os

print("🔍 בדיקת משתני סביבה ב-Railway:")
print("=" * 50)

env_vars = [
    "TELEGRAM_TOKEN",
    "PORT",
    "RAILWAY_PUBLIC_DOMAIN",
    "RAILWAY_STATIC_URL",
    "RAILWAY_ENVIRONMENT",
    "RAILWAY_SERVICE_NAME",
    "RAILWAY_PROJECT_NAME",
    "REDIS_URL"
]

for var in env_vars:
    value = os.environ.get(var, "❌ לא מוגדר")
    print(f"{var}: {value}")

print("=" * 50)
print("📋 אם RAILWAY_PUBLIC_DOMAIN לא מוגדר, הוסף אותו ב-Railway Variables")
