[CmdletBinding()]
param(
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

& (Join-Path $PSScriptRoot "scripts\local-server.ps1") -Action Stop -WhatIf:$WhatIf
