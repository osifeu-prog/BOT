# סקריפט בדיקות אוטומטיות
Write-Host "🧪 הרצת בדיקות NFTY PRO..." -ForegroundColor Yellow

# בדוק ייבואי Python
python -c "import sys; print(f'✅ Python {sys.version}')"
python -c "from config import TELEGRAM_TOKEN; print('✅ Config loaded')"
python -c "from app.database.manager import db; print('✅ Database connected')"

# בדוק קבצים קריטיים
$critical_files = @("Main.py", "config.py", "requirements.txt", "railway.json")
foreach ($file in $critical_files) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
    }
}

# הרץ בדיקת תחביר
python -m py_compile Main.py
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Main.py syntax OK" -ForegroundColor Green }

Write-Host "🎉 כל הבדיקות הושלמו!" -ForegroundColor Magenta
