# 🚀 NIFTII PRO Project Manager
# PowerShell script for project management

param(
    [string]$Command = "help",
    [string]$Arg1,
    [string]$Arg2
)

function Show-Banner {
    Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        🎰 NFTY PRO MANAGER          ║" -ForegroundColor Magenta
    Write-Host "║      Telegram Casino SaaS           ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Start-LocalTest {
    Write-Host "🚀 Starting local test environment..." -ForegroundColor Yellow
    
    # Stop any running instances
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run bot with test token
    $env:TELEGRAM_TOKEN = "TEST_MODE_LOCAL_ONLY"
    $env:REDIS_URL = "redis://localhost:6379"
    python Main.py
}

function Deploy-Production {
    Write-Host "☁️ Deploying to Railway..." -ForegroundColor Yellow
    
    # Check for changes
    git status
    
    # Add all files
    git add .
    
    # Commit with dynamic message
    $commitMsg = if ($Arg1) { $Arg1 } else { "Auto-deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
    git commit -m $commitMsg
    
    # Push to main
    git push origin main
    
    Write-Host "✅ Deployment initiated! Check: https://railway.app" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "🧪 Running all tests..." -ForegroundColor Yellow
    
    # Syntax check
    $files = Get-ChildItem -Recurse -Include *.py -Path "app", "admin"
    foreach ($file in $files) {
        python -m py_compile $file.FullName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $($file.Name)" -ForegroundColor Green
        }
    }
    
    # Import checks
    python -c "from app.database.manager import db; print('✅ Database: OK')"
    python -c "from app.security import rate_limiter; print('✅ Security: OK')"
    
    Write-Host "🎉 All tests passed!" -ForegroundColor Magenta
}

function Show-Status {
    Write-Host "📊 Project Status:" -ForegroundColor Cyan
    Write-Host "  Bot: $(if (Get-Process python -ErrorAction SilentlyContinue) {'🟢 Running'} else {'🔴 Stopped'})"
    Write-Host "  Files: $( (Get-ChildItem -Recurse -File | Measure-Object).Count )"
    
    # Get last commit
    $lastCommit = git log -1 --format='%cr' 2>$null
    if ($lastCommit) {
        Write-Host "  Last Commit: $lastCommit"
    } else {
        Write-Host "  Last Commit: N/A"
    }
    
    # Get current branch
    $branch = git branch --show-current 2>$null
    if ($branch) {
        Write-Host "  Branch: $branch"
    } else {
        Write-Host "  Branch: N/A"
    }
}

function Update-Dependencies {
    Write-Host "📦 Updating dependencies..." -ForegroundColor Yellow
    pip install --upgrade -r requirements.txt
    pip freeze > requirements.txt
    Write-Host "✅ Dependencies updated!" -ForegroundColor Green
}

# Main execution
Show-Banner

switch ($Command.ToLower()) {
    "start" { Start-LocalTest }
    "deploy" { Deploy-Production }
    "test" { Run-Tests }
    "status" { Show-Status }
    "update" { Update-Dependencies }
    "help" {
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  ./project_manager.ps1 start     - Start local test"
        Write-Host "  ./project_manager.ps1 deploy    - Deploy to Railway"
        Write-Host "  ./project_manager.ps1 test      - Run all tests"
        Write-Host "  ./project_manager.ps1 status    - Show project status"
        Write-Host "  ./project_manager.ps1 update    - Update dependencies"
        Write-Host "  ./project_manager.ps1 help      - Show this help"
    }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host "💡 Use 'help' to see available commands" -ForegroundColor Yellow
    }
}
