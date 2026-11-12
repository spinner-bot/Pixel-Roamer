@echo off
setlocal
cd /d "%~dp0"

rem Optional: set PIXEL_ROAMER_PYTHON to an interpreter that already has pygame.
if defined PIXEL_ROAMER_PYTHON goto run_override

rem Reuse an existing Python installation when pygame is already available.
python -c "import pygame" >nul 2>nul
if not errorlevel 1 goto run_python
py -3 -c "import pygame" >nul 2>nul
if not errorlevel 1 goto run_py3
python3 -c "import pygame" >nul 2>nul
if not errorlevel 1 goto run_python3

set "VENV_PY=%~dp0.venv\Scripts\python.exe"
if not exist "%VENV_PY%" goto create_venv
"%VENV_PY%" -c "import pygame" >nul 2>nul
if not errorlevel 1 goto run_venv
echo [Pixel Roamer] Local .venv is missing pygame; repairing it...
goto install_venv

:run_override
"%PIXEL_ROAMER_PYTHON%" main.py
if errorlevel 1 pause
exit /b 0

:run_python
python main.py
if errorlevel 1 pause
exit /b 0

:run_py3
py -3 main.py
if errorlevel 1 pause
exit /b 0

:run_python3
python3 main.py
if errorlevel 1 pause
exit /b 0

:create_venv
echo [Pixel Roamer] No Python with pygame found; creating a local .venv...

set "PY_CMD="
python --version >nul 2>nul && set "PY_CMD=python"
if not defined PY_CMD (
    py -3 --version >nul 2>nul && set "PY_CMD=py -3"
)
if not defined PY_CMD (
    python3 --version >nul 2>nul && set "PY_CMD=python3"
)
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
goto install_venv

:install_venv
echo [Pixel Roamer] Installing dependencies into .venv...
set "TMP=%~dp0.tmp"
set "TEMP=%~dp0.tmp"
if not exist "%TMP%" mkdir "%TMP%"
"%VENV_PY%" -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 goto install_failed

:run_venv
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
