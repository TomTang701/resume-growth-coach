$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

& (Join-Path $PSScriptRoot "scripts\ensure-ollama.ps1")

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    Write-Host "Virtual environment was not found." -ForegroundColor Red
    Write-Host "Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock"
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "`"$python`" -m uvicorn app.main:app --reload" -WorkingDirectory $PSScriptRoot

$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 "http://127.0.0.1:8000/health"
        if ($response.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "The server did not become ready at http://127.0.0.1:8000/health" -ForegroundColor Red
    exit 1
}

Start-Process "http://127.0.0.1:8000"
