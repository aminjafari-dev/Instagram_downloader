@echo off
setlocal
cd /d %~dp0\..

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found in PATH.
  pause
  exit /b 1
)

python -m pip show yt-dlp >nul 2>nul
if errorlevel 1 (
  echo Installing dependencies...
  pip install -r scripts\requirements.txt
)

python -m src.cli --gui

endlocal

