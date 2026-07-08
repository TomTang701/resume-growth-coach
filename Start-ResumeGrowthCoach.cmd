@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment was not found.
  echo Run: python -m venv .venv && .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

start "Resume Growth Coach" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000"

