#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$LocalOnly
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
$python = Join-Path $root ".venv\Scripts\python.exe"
$evidencePath = Join-Path $root "local_data\verification-evidence.json"
$verifiedCommit = [string](& git -C $root rev-parse HEAD 2>$null)
$gitExitCode = $LASTEXITCODE
if ($gitExitCode -ne 0 -or -not $verifiedCommit) {
    $verifiedCommit = $null
} else {
    $verifiedCommit = $verifiedCommit.Trim()
}
$worktreeClean = $true
& git -C $root diff --quiet
if ($LASTEXITCODE -ne 0) { $worktreeClean = $false }
& git -C $root diff --cached --quiet
if ($LASTEXITCODE -ne 0) { $worktreeClean = $false }
if (-not $worktreeClean) {
    Write-Warning "Tracked source changes are present; resume evidence remains ineligible until they are committed and verified."
}

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
    try {
        & (Join-Path $PSScriptRoot "run-docker-smoke.ps1") | Out-Host
        $dockerPassed = ($LASTEXITCODE -eq 0)
    } catch {
        Write-Warning "Docker Compose smoke test failed: $($_.Exception.Message)"
    }
}

$ciPassed = $false
if ($worktreeClean -and $verifiedCommit -and -not $LocalOnly -and (Get-Command gh -ErrorAction SilentlyContinue)) {
    $repoUrl = git -C $root remote get-url origin 2>$null
    $commit = $verifiedCommit
    if ($repoUrl -match "github\.com[:/](?<owner>[^/]+)/(?<name>[^/.]+)(\.git)?$") {
        $repoName = "$($Matches.owner)/$($Matches.name)"
        $runs = gh run list --repo $repoName --commit $commit --limit 1 --json status,conclusion | ConvertFrom-Json
        if ($runs.Count -eq 1 -and $runs[0].status -eq "completed" -and $runs[0].conclusion -eq "success") {
            $ciPassed = $true
        }
    }
}

$documentationComplete = (Test-Path -LiteralPath (Join-Path $root "README.md")) -and (Test-Path -LiteralPath (Join-Path $root "docs\TEST_REPORT.md"))
$sanitizedDemoVerified = (Test-Path -LiteralPath (Join-Path $root "samples\sanitized\resume.txt")) -and (Test-Path -LiteralPath (Join-Path $root "samples\sanitized\job_description.txt"))
$evidence = [ordered]@{
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    generated_by = "scripts/record-verification-evidence.ps1"
    verified_commit = $verifiedCommit
    worktree_clean = $worktreeClean
    tests_passed = ($testsPassed -and $qualityPassed -and $browserPassed)
    docker_smoke_passed = $dockerPassed
    ci_passed = $ciPassed
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
