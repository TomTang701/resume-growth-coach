@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment was not found.
  echo Run: python -m venv .venv && .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ensure-ollama.ps1"
if errorlevel 1 (
  echo Ollama could not be started or the local model is unavailable.
  pause
  exit /b 1
)

start "Resume Growth Coach" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload"
set "READY="
for /l %%i in (1,1,30) do (
  powershell -NoProfile -Command "try { if ((Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 http://127.0.0.1:8000/health).StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
  if not errorlevel 1 (
    set "READY=1"
    goto :ready
  )
  timeout /t 1 /nobreak >nul
)
:ready
if not defined READY (
  echo The server did not become ready at http://127.0.0.1:8000/health
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8000"
