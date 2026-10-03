#!/usr/bin/env bash
# ==============================================================================
# DigiSmartDeck - Runner untuk Linux & macOS
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  ⌨️  DigiSmartDeck - Remote PC Keyboard Server${NC}"
echo -e "${BLUE}============================================================${NC}"

# 1. Periksa ketersediaan Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] python3 tidak ditemukan. Harap instal Python 3 terlebih dahulu.${NC}"
    exit 1
fi

# 2. Periksa petunjuk khusus macOS (Accessibility Permission)
if [[ "$(uname -s)" == "Darwin" ]]; then
    echo -e "${YELLOW}[i] Menjalankan di macOS:${NC}"
    echo "    Pastikan Terminal/iTerm Anda memiliki izin 'Accessibility' di:"
    echo "    System Settings > Privacy & Security > Accessibility."
    echo ""
fi

# 3. Instal dependencies jika belum lengkap
python3 -c "import aiohttp, pynput, qrcode" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[i] Menginstal modul Python yang dibutuhkan...${NC}"
    python3 -m pip install -r requirements.txt --break-system-packages 2>/dev/null || python3 -m pip install -r requirements.txt
fi

# 4. Jalankan server
python3 server.py
