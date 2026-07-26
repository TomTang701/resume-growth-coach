#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("Start", "Stop", "Status")]
    [string]$Action,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$statePath = Join-Path $root "local_data\local-server.json"
$commandMarker = "uvicorn app.main:app"

function Get-ProcessTree {
    param([int]$RootPid)

    $allProcesses = @(Get-CimInstance Win32_Process)
    $childrenByParent = @{}
    foreach ($process in $allProcesses) {
        $parentId = [int]$process.ParentProcessId
        if (-not $childrenByParent.ContainsKey($parentId)) {
            $childrenByParent[$parentId] = New-Object System.Collections.Generic.List[int]
        }
        $childrenByParent[$parentId].Add([int]$process.ProcessId)
    }

    $pending = New-Object System.Collections.Generic.Queue[int]
    $seen = New-Object System.Collections.Generic.HashSet[int]
    $pending.Enqueue($RootPid)
    while ($pending.Count -gt 0) {
        $current = $pending.Dequeue()
        if (-not $seen.Add($current)) {
            continue
        }
        if ($childrenByParent.ContainsKey($current)) {
            foreach ($childId in $childrenByParent[$current]) {
                $pending.Enqueue($childId)
            }
        }
    }

    return @($seen)
}

function Get-RecordedServer {
    if (-not (Test-Path -LiteralPath $statePath)) {
        throw "No Resume Growth Coach local-server record exists at $statePath. Refusing to stop an unrecorded process."
    }

    try {
        $record = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        $rootPid = [int]$record.pid
    } catch {
        throw "The local-server record is invalid. Refusing to stop any process."
    }

    $rootProcess = @(Get-CimInstance Win32_Process -Filter "ProcessId = $rootPid") | Select-Object -First 1
    if ($null -eq $rootProcess) {
        throw "The recorded process $rootPid no longer exists. Refusing to stop any other process."
    }
    if ($rootProcess.Name -ine "python.exe") {
        throw "The recorded process is not the expected Python launcher. Refusing to stop it."
    }

    $commandLine = [string]$rootProcess.CommandLine
    if ($commandLine.IndexOf($python, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "The recorded Python process does not contain this checkout's Python path. Refusing to stop it."
    }
    if ($commandLine.IndexOf($commandMarker, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "The recorded Python process does not contain the expected Uvicorn command. Refusing to stop it."
    }
    if (-not (Test-Path -LiteralPath $python)) {
        throw "The expected local Python executable is missing. Refusing to stop without validating the record."
    }

    $encodedCommandLine = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($commandLine))
    & $python -m app.lifecycle --record-path $statePath --checkout $root --observed-command-base64 $encodedCommandLine
    if ($LASTEXITCODE -ne 0) {
        throw "The local-server record does not match this checkout and command. Refusing to stop it."
    }

    $treeIds = @(Get-ProcessTree -RootPid $rootPid)
    $listener = @(
        Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction Stop |
            Where-Object {
                $_.LocalAddress -in @("127.0.0.1", "::1") -and
                $treeIds -contains [int]$_.OwningProcess
            }
    ) | Select-Object -First 1
    if ($null -eq $listener) {
        throw "No loopback listener on port 8000 belongs to the recorded process tree. Refusing to stop it."
    }

    return [pscustomobject]@{
        Record = $record
        RootProcess = $rootProcess
        Listener = $listener
    }
}

function Start-RecordedServer {
    if (-not (Test-Path -LiteralPath $python)) {
        throw "Virtual environment was not found at $python. Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock"
    }

    $existingListener = @(Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalAddress -in @("127.0.0.1", "::1") })
    if ($existingListener.Count -gt 0) {
        throw "A loopback listener already owns port 8000. Refusing to create an ambiguous server record."
    }

    & (Join-Path $PSScriptRoot "ensure-ollama.ps1")

    $serverArguments = "-m uvicorn app.main:app --app-dir `"$root`" --reload"
    $process = Start-Process -FilePath $python -ArgumentList $serverArguments -WorkingDirectory $root -PassThru

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
        & taskkill.exe /PID $process.Id /T /F | Out-Null
        throw "The server did not become ready at http://127.0.0.1:8000/health"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $statePath) -Force | Out-Null
    $record = [ordered]@{
        pid = [int]$process.Id
        checkout = $root
        command_marker = $commandMarker
    }
    $record | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
    Write-Host "Resume Growth Coach is ready at http://127.0.0.1:8000 (recorded PID $($process.Id))."
}

switch ($Action) {
    "Start" {
        Start-RecordedServer
    }
    "Status" {
        $server = Get-RecordedServer
        Write-Host "Recorded Resume Growth Coach server: PID $($server.RootProcess.ProcessId), listener PID $($server.Listener.OwningProcess)."
    }
    "Stop" {
        $server = Get-RecordedServer
        $target = "recorded Resume Growth Coach process tree rooted at PID $($server.RootProcess.ProcessId)"
        if (-not $WhatIf) {
            & taskkill.exe /PID $server.RootProcess.ProcessId /T /F | Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "taskkill failed for the validated process tree."
            }
            Remove-Item -LiteralPath $statePath -Force
            Write-Host "Stopped Resume Growth Coach and removed its local-server record."
        } else {
            Write-Host "Validated $target; -WhatIf did not stop it."
        }
    }
}
