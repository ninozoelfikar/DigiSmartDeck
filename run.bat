@echo off
title Remote PC Keyboard Server
cd /d "%~dp0"

echo ==============================================
echo    Remote PC Keyboard Server untuk Windows
echo ==============================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python tidak ditemukan. Harap instal Python 3 dan centang "Add Python to PATH".
    pause
    exit /b 1
)

echo [i] Memeriksa dependencies...
python -m pip install -r requirements.txt

echo.
echo [i] Menjalankan server...
python server.py

pause
