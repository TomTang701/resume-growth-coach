#requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Desktop is required for this smoke test."
    exit 1
}

try {
    docker compose up --build -d
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    $healthy = $false
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
            if ($response.StatusCode -eq 200 -and $response.Content -match '"status":"ok"') {
                $healthy = $true
                break
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    if (-not $healthy) {
        docker compose logs
        throw "Docker service did not become healthy."
    }
    & (Join-Path $PSScriptRoot "assert-local-port-bindings.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Compose loopback port binding check failed with exit code $LASTEXITCODE." }
    Write-Host "Docker smoke test passed." -ForegroundColor Green
} finally {
    docker compose down --volumes --remove-orphans
}
