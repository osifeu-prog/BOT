# Test script
Write-Host "🧪 Running NFTY PRO tests..." -ForegroundColor Yellow

# Check Python imports
python -c "import sys; print(f'✅ Python {sys.version}')"
python -c "from config import TELEGRAM_TOKEN; print('✅ Config loaded')"
python -c "from app.database.manager import db; print('✅ Database connected')"

# Check critical files
$critical_files = @("Main.py", "config.py", "requirements.txt", "railway.json")
foreach ($file in $critical_files) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
    }
}

# Syntax check
python -m py_compile Main.py
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Main.py syntax OK" -ForegroundColor Green }

Write-Host "🎉 All tests completed!" -ForegroundColor Magenta
