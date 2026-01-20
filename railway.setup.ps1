# 🚂 Railway Setup Script

Write-Host "🚂 Setting up Railway environment..." -ForegroundColor Cyan

# 1. התקן Railway CLI (אם חסר)
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Railway CLI..." -ForegroundColor Yellow
    winget install railway
}

# 2. התחבר ל-Railway
railway login

# 3. צור פרויקט חדש או התחבר לקיים
Write-Host "🔗 Connecting to Railway project..." -ForegroundColor Yellow
railway link

# 4. הגדר משתני סביבה
$envVars = @{
    "TELEGRAM_TOKEN" = "YOUR_BOT_TOKEN_HERE";
    "REDIS_URL" = "redis://:password@host:port";
    "ADMIN_ID" = "YOUR_TELEGRAM_ID";
    "CRYPTO_PAY_TOKEN" = "YOUR_CRYPTOBOT_TOKEN";
    "PARTICIPANTS_GROUP_LINK" = "https://t.me/your_group";
    "BOT_USERNAME" = "@YourBotUsername";
    "WIN_CHANCE_PERCENT" = "80";
    "REFERRAL_REWARD" = "500"
}

Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
foreach ($key in $envVars.Keys) {
    railway variables set $key $envVars[$key]
    Write-Host "  ✅ $key" -ForegroundColor Green
}

# 5. הרץ דפלוי ראשון
Write-Host "🚀 Deploying first version..." -ForegroundColor Magenta
railway up

Write-Host "🎉 Railway setup complete!" -ForegroundColor Green
Write-Host "🌐 Your bot URL: https://railway.app/project/your-project" -ForegroundColor Cyan
Write-Host "🤖 Bot link: https://t.me/YourBotUsername" -ForegroundColor Magenta
