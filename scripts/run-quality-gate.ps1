$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    Write-Host "Virtual environment was not found at $python" -ForegroundColor Red
    exit 1
}

& $python "tools\quality_gate.py"
exit $LASTEXITCODE
