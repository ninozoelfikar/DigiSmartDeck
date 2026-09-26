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

# ── 3. Cek Display/X11 untuk pynput ──
echo -e "${CYAN}[3/4]${NC} Memeriksa akses keyboard (X11/Wayland)..."

if python3 -c "
from pynput.keyboard import Controller, Key
c = Controller()
print('OK')
" 2>/dev/null | grep -q "OK"; then
    echo -e "    ${GREEN}✓ Kontrol keyboard aktif - input akan dikirim ke PC${NC}"
else
    echo -e "    ${YELLOW}⚠ Display server tidak terdeteksi.${NC}"
    echo "    Tips:"
    echo "    • Pastikan Anda menjalankan script ini dari terminal di dalam sesi desktop GUI."
    echo "    • Jika menggunakan SSH, tambahkan: export DISPLAY=:0"
    echo ""
    echo -e "    ${YELLOW}Server tetap akan berjalan (mode log/simulasi).${NC}"
fi

# ── 4. Deteksi IP ──
echo -e "${CYAN}[4/4]${NC} Mendeteksi alamat IP jaringan lokal..."
LOCAL_IP=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    print(s.getsockname()[0])
    s.close()
except: print('127.0.0.1')
")
echo -e "    ${GREEN}✓ IP PC Anda: ${LOCAL_IP}${NC}"
echo ""

# ── Firewall Info ──
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}[INFO FIREWALL]${NC}"
echo "Jika HP tidak bisa terhubung, buka port 8080 di firewall:"
echo ""
if command -v ufw &>/dev/null; then
    echo "  Ubuntu/Debian (ufw):"
    echo -e "  ${CYAN}sudo ufw allow 8080/tcp${NC}"
elif command -v firewall-cmd &>/dev/null; then
    echo "  Fedora/RHEL (firewalld):"
    echo -e "  ${CYAN}sudo firewall-cmd --add-port=8080/tcp --permanent && sudo firewall-cmd --reload${NC}"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Menjalankan DigiKeyboard Server...${NC}"
echo -e "Buka di HP/Tablet: ${CYAN}http://${LOCAL_IP}:8080${NC}"
echo ""

# ── Jalankan Server ──
cd "$SCRIPT_DIR"
python3 server.py
