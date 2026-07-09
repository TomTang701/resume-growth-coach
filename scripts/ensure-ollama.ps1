param(
    [string]$Model = "qwen2.5:3b",
    [int]$Port = 11434
)

$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:$Port"
$tagsUrl = "$baseUrl/api/tags"

function Get-OllamaExecutable {
    $command = Get-Command ollama -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $defaultPath = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path -LiteralPath $defaultPath) {
        return $defaultPath
    }

    throw "Ollama was not found. Install it from https://ollama.com/download/windows."
}

function Test-OllamaApi {
    try {
        $response = Invoke-RestMethod -Uri $tagsUrl -Method Get -TimeoutSec 2
        return $null -ne $response
    } catch {
        return $false
    }
}

function Test-OllamaGeneration {
    try {
        $payload = @{ model = $Model; prompt = "Reply with OK."; stream = $false } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$baseUrl/api/generate" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 120
        return $null -ne $response -and $null -ne $response.response
    } catch {
        return $false
    }
}

$ollama = Get-OllamaExecutable

if (-not (Test-OllamaApi)) {
    Write-Host "Starting Ollama service..."
    Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden
}

$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    if (Test-OllamaApi) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 1
}

if (-not $ready) {
    throw "Ollama API did not become ready at $tagsUrl."
}

$modelsResponse = Invoke-RestMethod -Uri $tagsUrl -Method Get -TimeoutSec 5
$modelNames = @($modelsResponse.models | ForEach-Object { $_.name })
if ($modelNames -notcontains $Model) {
    Write-Host "Model $Model was not found. Pulling it now..."
    & $ollama pull $Model
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to pull Ollama model $Model."
    }
}

if (-not (Test-OllamaGeneration)) {
    throw "Ollama model $Model is installed but could not complete a generation request."
}

Write-Host "Ollama is ready with model $Model."
