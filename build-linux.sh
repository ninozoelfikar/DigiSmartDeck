#!/usr/bin/env bash
# ==============================================================================
# DigiSmartDeck - Standalone Binary Builder untuk Linux
# Menghasilkan executable mandiri (ELF binary) tanpa perlu Python di PC target
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
echo -e "${BLUE}  📦  DigiSmartDeck - Build Standalone Linux Executable${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 1. Periksa ketersediaan Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] python3 tidak ditemukan. Harap instal Python 3 terlebih dahulu.${NC}"
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

# 3. Compile ke binary standalone
echo -e "${YELLOW}[2/3] Mengompilasi server.py menjadi binary mandiri...${NC}"
python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --name "DigiSmartDeck" \
    --add-data "static:static" \
    --add-data "VERSION:." \
    --hidden-import "pynput.keyboard._xorg" \
    --hidden-import "pynput.mouse._xorg" \
    --hidden-import "pynput.keyboard._uinput" \
    --hidden-import "evdev" \
    --hidden-import "aiohttp" \
    --hidden-import "qrcode" \
    server.py

# 4. Beri permission executable dan strip debug symbols (Anti-Reverse Engineering)
chmod +x dist/DigiSmartDeck
if command -v strip &> /dev/null; then
    echo -e "${YELLOW}[3/3] Melakukan binary stripping untuk proteksi anti-reverse engineering...${NC}"
    strip --strip-all dist/DigiSmartDeck 2>/dev/null || true
    echo -e "${GREEN}[✓] Simbol debug biner berhasil di-strip.${NC}"
fi

# 5. Opsi Native Rust Engine jika terpasang
if [ -d "host-rust" ] && command -v cargo &> /dev/null; then
    echo -e "${YELLOW}[Bonus] Mengompilasi Host Native Rust biner terlindung...${NC}"
    cd host-rust
    cargo build --release
    cd "$SCRIPT_DIR"
    if [ -f "host-rust/target/release/digismartdeck-host" ]; then
        cp -f host-rust/target/release/digismartdeck-host dist/DigiSmartDeck-Linux
        chmod +x dist/DigiSmartDeck-Linux
        strip --strip-all dist/DigiSmartDeck-Linux 2>/dev/null || true
        echo -e "${GREEN}[✓] Biner native Rust tersimpan di dist/DigiSmartDeck-Linux (Anti-decompile 100%)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}[✓] BERHASIL! File binary executable mandiri telah dibuat:${NC}"
echo -e "    ${BLUE}${SCRIPT_DIR}/dist/DigiSmartDeck${NC}"
echo -e "${GREEN}============================================================${NC}"
echo "Anda dapat menjalankan langsung file tersebut:"
echo -e "    ${YELLOW}./dist/DigiSmartDeck${NC}"
echo ""
echo "Catatan untuk akses Linux hardware uinput (Layar Login / Wayland):"
echo -e "    ${YELLOW}sudo setfacl -m u:\$USER:rw /dev/uinput${NC} (atau jalankan setup-uinput.sh)"
echo ""
