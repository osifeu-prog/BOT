# 🚂 Railway Setup Script

Write-Host "🚂 Setting up Railway environment..." -ForegroundColor Cyan

# 1. Install Railway CLI (if missing)
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Railway CLI..." -ForegroundColor Yellow
    winget install railway
}

# 2. Login to Railway
railway login

# 3. Create new project or connect to existing
Write-Host "🔗 Connecting to Railway project..." -ForegroundColor Yellow
railway link

# 4. Set environment variables
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

# 5. Run first deploy
Write-Host "🚀 Deploying first version..." -ForegroundColor Magenta
railway up

Write-Host "🎉 Railway setup complete!" -ForegroundColor Green
Write-Host "🌐 Your bot URL: https://railway.app/project/your-project" -ForegroundColor Cyan
Write-Host "🤖 Bot link: https://t.me/YourBotUsername" -ForegroundColor Magenta
