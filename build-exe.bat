@echo off
setlocal enabledelayedexpansion
title DigiSmartDeck - Build Windows EXE
cd /d "%~dp0"

echo ============================================================
echo   📦  DigiSmartDeck - Build Standalone Windows EXE
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

echo [✓] Menggunakan Python: %PYCMD%
echo.

echo [1/3] Memeriksa & menginstal dependencies dan PyInstaller...
%PYCMD% -m pip install --upgrade pip
%PYCMD% -m pip install -r requirements.txt pyinstaller
if %errorlevel% neq 0 (
    echo [!] Gagal menginstal dependencies atau PyInstaller.
    pause
    exit /b 1
)

echo.
echo [2/3] Memulai proses compile ke file EXE...
%PYCMD% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --console ^
    --name "DigiSmartDeck" ^
    --icon "static/icon.ico" ^
    --add-data "static;static" ^
    --add-data "VERSION;." ^
    --hidden-import "pynput.keyboard._win32" ^
    --hidden-import "pynput.mouse._win32" ^
    --hidden-import "aiohttp" ^
    --hidden-import "qrcode" ^
    server.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Terjadi kesalahan saat proses compile PyInstaller.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [✓] BERHASIL! File executable telah dibuat:
echo     dist\DigiSmartDeck.exe
echo ============================================================
echo Anda dapat menyalin file "dist\DigiSmartDeck.exe" dan langsung
echo menjalankannya di komputer Windows mana saja tanpa perlu instal Python!
echo.
pause
