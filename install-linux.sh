#!/usr/bin/env bash
# ================================================================
#  DigiKeyboard - Installer & Launcher untuk Linux PC
#  Jalankan script ini di PC/Laptop Linux yang terhubung ke WiFi
#  yang sama dengan HP/Tablet Anda.
# ================================================================

set -e
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${CYAN}"
echo "  ██████╗ ██╗ ██████╗ ██╗██╗  ██╗███████╗██╗   ██╗"
echo "  ██╔══██╗██║██╔════╝ ██║██║ ██╔╝██╔════╝╚██╗ ██╔╝"
echo "  ██║  ██║██║██║  ███╗██║█████╔╝ █████╗   ╚████╔╝ "
echo "  ██║  ██║██║██║   ██║██║██╔═██╗ ██╔══╝    ╚██╔╝  "
echo "  ██████╔╝██║╚██████╔╝██║██║  ██╗███████╗   ██║   "
echo "  ╚═════╝ ╚═╝ ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝  "
echo -e "${NC}"
echo -e "${GREEN}  Remote PC Keyboard - Linux Installer${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Cek Python ──
echo -e "${CYAN}[1/4]${NC} Memeriksa Python 3..."
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}Python3 tidak ditemukan. Mencoba instal...${NC}"
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy python python-pip
    else
        echo -e "${RED}[!] Harap instal Python 3 manual lalu jalankan script ini lagi.${NC}"
        exit 1
    fi
fi
echo -e "    ${GREEN}✓ Python $(python3 --version | cut -d' ' -f2)${NC}"

# ── 2. Install dependencies ──
echo -e "${CYAN}[2/4]${NC} Menginstal dependencies Python..."

PIP_FLAGS=""
# Deteksi apakah perlu --break-system-packages (Python 3.11+)
if python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
    PIP_FLAGS="--break-system-packages"
fi

# Check & install dependencies
MISSING_PKGS=""
python3 -c "import aiohttp" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS aiohttp"
python3 -c "import pynput" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS pynput"
python3 -c "import qrcode" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS qrcode"

if [ -n "$MISSING_PKGS" ]; then
    echo "    Menginstal:$MISSING_PKGS"
    python3 -m pip install $MISSING_PKGS $PIP_FLAGS -q
else
    echo -e "    ${GREEN}✓ Semua dependencies sudah terinstal${NC}"
fi

# ── 3. Pemeriksaan Izin Sistem & Kesiapan (Ramah Awam) ──
echo -e "${CYAN}[3/4]${NC} Memeriksa kesiapan sistem & izin akses..."
python3 system_checker.py

# ── 4. Jalankan Server jika belum aktif ──
if ! python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/version', timeout=1)" 2>/dev/null; then
    echo -e "${GREEN}Menjalankan DigiKeyboard Server...${NC}"
    cd "$SCRIPT_DIR"
    python3 server.py
fi
