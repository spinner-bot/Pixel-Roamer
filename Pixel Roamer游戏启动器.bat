@echo off
setlocal
cd /d "%~dp0"

set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if exist "%VENV_PY%" goto run

echo [Pixel Roamer] First run: creating local virtual environment...

set "PY_CMD="
python --version >nul 2>nul && set "PY_CMD=python"
if not defined PY_CMD py -3 --version >nul 2>nul && set "PY_CMD=py -3"
if not defined PY_CMD (
    echo [Pixel Roamer] Python 3.10+ was not found.
    echo Install it from https://www.python.org/downloads/ and run this file again.
    pause
    exit /b 1
)

rem Keep temporary files on the project drive; the system temp drive may be full.
set "TMP=%~dp0.tmp"
set "TEMP=%~dp0.tmp"
if not exist "%TMP%" mkdir "%TMP%"

%PY_CMD% -m venv ".venv"
if errorlevel 1 goto venv_failed

echo [Pixel Roamer] Installing dependencies...
"%VENV_PY%" -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 goto install_failed

:run
"%VENV_PY%" main.py
if errorlevel 1 pause
exit /b 0

:venv_failed
echo [Pixel Roamer] Failed to create .venv.
pause
exit /b 1

:install_failed
echo [Pixel Roamer] Failed to install requirements. Check your network and run this file again.
pause
exit /b 1
