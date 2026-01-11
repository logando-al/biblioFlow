# BiblioFlow Development Setup Script
# Run this in PowerShell: .\setup.ps1

Write-Host "BiblioFlow Development Setup" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/4] Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -r requirements-dev.txt --quiet

Write-Host "[4/4] Verifying installation..." -ForegroundColor Yellow
python -c "import PyQt6; print('PyQt6:', PyQt6.__version__)"

Write-Host "`n Setup complete!" -ForegroundColor Green
Write-Host "`nTo run the app:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python main.py"
Write-Host "`nTo run tests:" -ForegroundColor Cyan
Write-Host "  pytest tests/ -v"
