@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Stop-ResumeGrowthCoach.ps1" %*
if errorlevel 1 (
  echo Resume Growth Coach was not stopped. Review the validation message above.
  pause
  exit /b 1
)
