@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py valheim_host.py --config config.json host
  pause
  exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
  python valheim_host.py --config config.json host
  pause
  exit /b %errorlevel%
)

echo No encontre Python instalado.
echo Instala Python desde https://www.python.org/downloads/ y marca "Add python.exe to PATH".
pause
exit /b 1
