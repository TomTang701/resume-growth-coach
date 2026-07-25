#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$LocalOnly,
    [switch]$CiPassed
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
$python = Join-Path $root ".venv\Scripts\python.exe"
$evidencePath = Join-Path $root "local_data\verification-evidence.json"

if (-not (Test-Path -LiteralPath $python)) {
    Write-Error "Virtual environment was not found at $python"
    exit 1
}

function Invoke-Check {
    param(
        [string]$Executable,
        [string[]]$Arguments
    )
    & $Executable @Arguments | Out-Host
    $exitCode = $LASTEXITCODE
    return ($exitCode -eq 0)
}

$testsPassed = Invoke-Check -Executable $python -Arguments @("-m", "pytest", "-q")
$qualityPassed = Invoke-Check -Executable $python -Arguments @("tools\quality_gate.py")
$browserPassed = Invoke-Check -Executable $python -Arguments @("tools\browser_smoke.py")
$dockerPassed = $false
if (-not $LocalOnly) {
    $dockerPassed = Invoke-Check -Executable "powershell.exe" -Arguments @("-NoLogo", "-NoProfile", "-NonInteractive", "-File", (Join-Path $root "scripts\run-docker-smoke.ps1"))
}

$documentationComplete = (Test-Path -LiteralPath (Join-Path $root "README.md")) -and (Test-Path -LiteralPath (Join-Path $root "docs\TEST_REPORT.md"))
$sanitizedDemoVerified = (Test-Path -LiteralPath (Join-Path $root "samples\sanitized\resume.txt")) -and (Test-Path -LiteralPath (Join-Path $root "samples\sanitized\job_description.txt"))
$evidence = [ordered]@{
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    generated_by = "scripts/record-verification-evidence.ps1"
    tests_passed = ($testsPassed -and $qualityPassed -and $browserPassed)
    docker_smoke_passed = $dockerPassed
    ci_passed = $CiPassed.IsPresent
    documentation_complete = $documentationComplete
    sanitized_demo_verified = $sanitizedDemoVerified
}

New-Item -ItemType Directory -Path (Split-Path -Parent $evidencePath) -Force | Out-Null
$evidence | ConvertTo-Json | Set-Content -LiteralPath $evidencePath -Encoding utf8
Write-Host "Verification evidence written to $evidencePath"

if ($evidence.tests_passed -and $evidence.docker_smoke_passed -and $evidence.ci_passed -and $evidence.documentation_complete -and $evidence.sanitized_demo_verified) {
    Write-Host "Resume evidence gate passed." -ForegroundColor Green
    exit 0
}

Write-Host "Resume evidence gate is incomplete; no resume bullet is eligible." -ForegroundColor Yellow
exit 1
