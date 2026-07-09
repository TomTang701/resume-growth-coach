param(
    [string]$Model = "qwen2.5:3b",
    [int]$Port = 11434
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "ensure-ollama.ps1") -Model $Model -Port $Port
if (-not $?) {
    throw "Ollama readiness check failed."
}

$payload = @{ model = $Model; prompt = "Reply with exactly: OK"; stream = $false } | ConvertTo-Json
$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:$Port/api/generate" `
    -Method Post `
    -ContentType "application/json" `
    -Body $payload `
    -TimeoutSec 120

if ($response.model -and $response.model -ne $Model) {
    throw "Ollama responded with model $($response.model), expected $Model."
}
if (-not $response.response) {
    throw "Ollama returned an empty response."
}

Write-Host "Ollama smoke test passed with model $Model."
