@echo off
setlocal enabledelayedexpansion
title DigiKeyboard - Remote PC Keyboard Server
cd /d "%~dp0"

echo ============================================================
echo   ⌨️  DigiKeyboard - Remote PC Keyboard Server (Windows)
echo ============================================================
echo.

set PYCMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYCMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYCMD=py -3
    )
)

if "%PYCMD%"=="" (
    echo [!] Python 3 tidak ditemukan di sistem Windows Anda.
    echo     Silakan unduh dan instal Python dari https://www.python.org/
    echo     PENTING: Centang kotak "Add Python to PATH" saat instalasi.
    echo.
    pause
    exit /b 1
)

echo [✓] Menggunakan: %PYCMD%
echo [i] Memeriksa paket Python...
%PYCMD% -c "import aiohttp, pynput, qrcode" >nul 2>nul
if %errorlevel% neq 0 (
    echo [i] Menginstal dependencies (aiohttp, pynput, qrcode)...
    %PYCMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [!] Gagal menginstal dependencies. Periksa koneksi internet Anda.
        pause
        exit /b 1
    )
)

echo.
echo [i] Menjalankan server DigiKeyboard...
%PYCMD% server.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Server berhenti dengan kode error %errorlevel%.
)

pause
