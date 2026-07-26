#requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$containerLines = @(docker compose ps -q app)
if ($LASTEXITCODE -ne 0 -or $containerLines.Count -ne 1) {
    throw "Expected exactly one running container for service 'app'."
}
$containerId = ([string]$containerLines[0]).Trim()
$portJsonLines = @(docker inspect $containerId --format '{{json .NetworkSettings.Ports}}')
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect port bindings for service 'app'."
}
$portMappings = (($portJsonLines -join "`n") | ConvertFrom-Json)
$bindings = @($portMappings.PSObject.Properties["8000/tcp"].Value)
if ($bindings.Count -eq 0) {
    throw "Service 'app' does not publish 8000/tcp."
}
foreach ($binding in $bindings) {
    if ($binding.HostIp -ne "127.0.0.1" -or [string]$binding.HostPort -ne "8000") {
        throw "Service 'app' must bind 8000/tcp only to 127.0.0.1:8000, but Docker reported $($binding.HostIp):$($binding.HostPort)."
    }
}

Write-Host "Compose port is bound only to loopback." -ForegroundColor Green
