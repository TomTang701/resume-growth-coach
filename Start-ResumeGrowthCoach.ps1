$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    Write-Host "Virtual environment was not found." -ForegroundColor Red
    Write-Host "Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "`"$python`" -m uvicorn app.main:app --reload" -WorkingDirectory $PSScriptRoot
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8000"

