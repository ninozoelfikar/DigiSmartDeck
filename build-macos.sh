#!/usr/bin/env bash
# ==============================================================================
# DigiKeyboard - Standalone App & Binary Builder untuk macOS
# Menghasilkan .app bundle dan binary mandiri tanpa perlu Python di PC target
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  🍏  DigiKeyboard - Build macOS App & Standalone Executable${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 1. Periksa ketersediaan Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] python3 tidak ditemukan. Harap instal Python 3 via brew atau python.org.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Python 3 ditemukan: $(python3 --version)${NC}"

# 2. Instal dependensi dan PyInstaller
echo -e "${YELLOW}[1/3] Memeriksa & menginstal requirements dan PyInstaller...${NC}"
python3 -m pip install -r requirements.txt pyinstaller --break-system-packages 2>/dev/null || \
python3 -m pip install --user -r requirements.txt pyinstaller || \
python3 -m pip install -r requirements.txt pyinstaller

# Pastikan PyInstaller terpasang
if ! python3 -m PyInstaller --version &> /dev/null; then
    echo -e "${RED}[!] Gagal menginstal PyInstaller. Silakan jalankan 'pip install pyinstaller'.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] PyInstaller versi: $(python3 -m PyInstaller --version)${NC}"

ICON_OPT=()
if [ -f "static/icon.icns" ]; then
    ICON_OPT=(--icon "static/icon.icns")
fi

# 3. Build Standalone CLI Binary
echo -e "${YELLOW}[2/3] Mengompilasi server.py menjadi binary mandiri...${NC}"
python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --name "DigiKeyboard" \
    "${ICON_OPT[@]}" \
    --add-data "static:static" \
    --add-data "VERSION:." \
    --osx-bundle-identifier "com.digikeyboard.remote" \
    --hidden-import "pynput.keyboard._darwin" \
    --hidden-import "pynput.mouse._darwin" \
    --hidden-import "aiohttp" \
    --hidden-import "qrcode" \
    server.py

# 4. Build .app Bundle
echo -e "${YELLOW}[3/3] Mengompilasi DigiKeyboard.app bundle (untuk GUI/Finder)...${NC}"
python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "DigiKeyboardApp" \
    "${ICON_OPT[@]}" \
    --add-data "static:static" \
    --add-data "VERSION:." \
    --osx-bundle-identifier "com.digikeyboard.app" \
    --hidden-import "pynput.keyboard._darwin" \
    --hidden-import "pynput.mouse._darwin" \
    --hidden-import "aiohttp" \
    --hidden-import "qrcode" \
    server.py

chmod +x dist/DigiKeyboard

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}[✓] BERHASIL! File executable macOS telah dibuat di folder dist/:${NC}"
echo -e "    1. Binary Terminal:  ${BLUE}${SCRIPT_DIR}/dist/DigiKeyboard${NC}"
echo -e "    2. macOS App Bundle: ${BLUE}${SCRIPT_DIR}/dist/DigiKeyboardApp.app${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${YELLOW}[i] PENTING untuk macOS:${NC}"
echo "    Beri izin 'Accessibility' di:"
echo "    System Settings > Privacy & Security > Accessibility"
echo "    untuk Terminal / DigiKeyboardApp agar keyboard & mouse dapat dikontrol."
echo ""
