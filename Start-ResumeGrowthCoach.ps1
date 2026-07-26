$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

& (Join-Path $PSScriptRoot "scripts\local-server.ps1") -Action Start

Start-Process "http://127.0.0.1:8000"
