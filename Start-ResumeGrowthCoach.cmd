@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-ResumeGrowthCoach.ps1"
if errorlevel 1 (
  echo Resume Growth Coach could not be started.
  pause
  exit /b 1
)
