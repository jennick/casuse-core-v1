# scripts/dev-test.ps1
# Schone venv + deps + tests; gebruikt Python 3.10 als die op PATH staat.
$ErrorActionPreference = "Stop"

Write-Host "==> Create fresh venv (.venv)" -ForegroundColor Cyan
if (Test-Path .\.venv) { Remove-Item -Recurse -Force .\.venv }
python -V
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "==> Install runtime deps" -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install -r core-backend\requirements.txt

Write-Host "==> Install dev/test deps" -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install -r core-backend\requirements-dev.txt

Write-Host "==> Run tests (venv python -m pytest)" -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pytest -q core-backend\tests
