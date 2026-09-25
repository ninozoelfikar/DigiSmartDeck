#!/usr/bin/env bash
# Remote PC Keyboard Runner for Linux / macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Menjalankan Remote PC Keyboard Server ==="

# Periksa apakah python3 tersedia
if ! command -v python3 &> /dev/null; then
    echo "[!] python3 tidak ditemukan. Harap instal Python 3 terlebih dahulu."
    exit 1
fi

# Instal dependencies jika belum ada
python3 -c "import aiohttp, pynput, qrcode" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[i] Menginstal modul yang dibutuhkan..."
    python3 -m pip install -r requirements.txt --break-system-packages 2>/dev/null || python3 -m pip install -r requirements.txt
fi

# Jalankan server
python3 server.py
