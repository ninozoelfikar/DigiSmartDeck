#!/usr/bin/env bash
# ================================================================
#  DigiSmartDeck - Installer & Launcher untuk Linux PC
#  Jalankan script ini di PC/Laptop Linux yang terhubung ke WiFi
#  yang sama dengan HP/Tablet Anda.
# ================================================================

set -e
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${CYAN}"
echo "  DIGISMARTDECK HOST & DESKTOP SUITE"
echo "  Pusat Kendali Keyboard, Touchpad & AI Workstation"
echo -e "${NC}"
echo -e "${GREEN}  Remote PC Keyboard - Linux Installer & Setup Wizard${NC}"
echo "--------------------------------------------------"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Cek Python ──
echo -e "${CYAN}[1/5]${NC} Memeriksa Python 3..."
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
echo -e "    ${GREEN}[OK] Python $(python3 --version | cut -d' ' -f2)${NC}"

# ── 2. Install dependencies ──
echo -e "${CYAN}[2/5]${NC} Menginstal dependencies Python..."

PIP_FLAGS=""
if python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
    PIP_FLAGS="--break-system-packages"
fi

MISSING_PKGS=""
python3 -c "import aiohttp" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS aiohttp"
python3 -c "import pynput" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS pynput"
python3 -c "import qrcode" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS qrcode"
python3 -c "import PIL" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS Pillow"
python3 -c "import PyQt5" 2>/dev/null || MISSING_PKGS="$MISSING_PKGS PyQt5"

if [ -n "$MISSING_PKGS" ]; then
    echo "    Menginstal:$MISSING_PKGS"
    python3 -m pip install $MISSING_PKGS $PIP_FLAGS -q
else
    echo -e "    ${GREEN}[OK] Semua dependencies sudah terinstal.${NC}"
fi

# ── 3. Pemeriksaan Izin Sistem & Kesiapan ──
echo -e "${CYAN}[3/5]${NC} Memeriksa kesiapan sistem & izin akses..."
if [ -f "$SCRIPT_DIR/system_checker.py" ]; then
    python3 "$SCRIPT_DIR/system_checker.py" || true
fi

# ── 4. Pasang Pintasan Desktop Linux ──
echo -e "${CYAN}[4/5]${NC} Memasang pintasan desktop dan menu aplikasi..."
mkdir -p ~/.local/share/applications ~/Desktop ~/.local/bin

cat > ~/.local/share/applications/digismartdeck.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=DigiSmartDeck
GenericName=Remote Keyboard & AI Workstation
Comment=DigiSmartDeck PC Host Manager and Device Pairing
Exec=/usr/bin/python3 /home/nino/digikeyboard/digikeyboard_gui.py
Path=/home/nino/digikeyboard
Icon=/home/nino/digikeyboard/assets/icon.png
Terminal=false
Categories=Utility;HardwareSettings;
StartupNotify=true
StartupWMClass=DigiSmartDeck Host
EOF

cp ~/.local/share/applications/digismartdeck.desktop ~/.local/share/applications/digikeyboard.desktop 2>/dev/null || true
cp ~/.local/share/applications/digismartdeck.desktop ~/Desktop/ 2>/dev/null || true
cp ~/.local/share/applications/digismartdeck.desktop ~/Desktop/digikeyboard.desktop 2>/dev/null || true
chmod +x ~/.local/share/applications/digismartdeck.desktop ~/Desktop/digismartdeck.desktop 2>/dev/null || true
gio set ~/Desktop/digismartdeck.desktop metadata::trusted true 2>/dev/null || true
ln -sf "$SCRIPT_DIR/digikeyboard_gui.py" ~/.local/bin/digismartdeck 2>/dev/null || true
ln -sf "$SCRIPT_DIR/digikeyboard_gui.py" ~/.local/bin/digikeyboard 2>/dev/null || true
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
echo -e "    ${GREEN}[OK] Pintasan desktop dan menu aplikasi terpasang.${NC}"

# ── 5. Integrasi Smart Terminal Otomatis ──
echo -e "${CYAN}[5/6]${NC} Menyiapkan integrasi Smart Terminal..."
mkdir -p ~/.config/digismartdeck ~/.local/bin
ln -sf "$SCRIPT_DIR/digi-term" ~/.local/bin/digi-term
chmod +x "$SCRIPT_DIR/digi-term" ~/.local/bin/digi-term

HOOK_LINE='if [[ $- == *i* && -t 0 && -t 1 && -z "$DIGI_TERM_SUPERVISED" && -z "$DIGI_TERM_DISABLE" && -f "$HOME/.config/digismartdeck/smart_terminal_enabled" && -x "$HOME/.local/bin/digi-term" ]]; then exec "$HOME/.local/bin/digi-term"; fi'

if [ -f "$HOME/.bashrc" ] && ! grep -q "DIGI_TERM_SUPERVISED" "$HOME/.bashrc"; then
    echo "" >> "$HOME/.bashrc"
    echo "# DigiSmartDeck Smart Terminal Integration" >> "$HOME/.bashrc"
    echo "$HOOK_LINE" >> "$HOME/.bashrc"
fi

if [ -f "$HOME/.zshrc" ] && ! grep -q "DIGI_TERM_SUPERVISED" "$HOME/.zshrc"; then
    echo "" >> "$HOME/.zshrc"
    echo "# DigiSmartDeck Smart Terminal Integration" >> "$HOME/.zshrc"
    echo "$HOOK_LINE" >> "$HOME/.zshrc"
fi

ENABLE_TERM="y"
if [ -t 0 ]; then
    echo ""
    echo -e "${YELLOW}Integrasi Smart Terminal:${NC}"
    echo "  Apakah Anda ingin mengaktifkan Smart Terminal otomatis?"
    echo "  Seluruh terminal yang dibuka di PC ini otomatis terhubung ke ponsel"
    echo "  sehingga pertanyaan konfirmasi (Yes/No, Allow AI, dsb) muncul di HP."
    read -p "  Aktifkan Smart Terminal otomatis? [Y/n]: " user_choice
    if [[ "$user_choice" =~ ^[Nn] ]]; then
        ENABLE_TERM="n"
    fi
fi

if [ "$ENABLE_TERM" = "y" ]; then
    touch "$HOME/.config/digismartdeck/smart_terminal_enabled"
    echo -e "    ${GREEN}[OK] Smart Terminal otomatis diaktifkan.${NC}"
else
    rm -f "$HOME/.config/digismartdeck/smart_terminal_enabled"
    echo -e "    ${YELLOW}[INFO] Smart Terminal dinonaktifkan (dapat diaktifkan nanti di Host Manager).${NC}"
fi

# ── 6. Jalankan Aplikasi GUI Host Manager atau Server Background ──
echo -e "${CYAN}[6/6]${NC} Menjalankan DigiSmartDeck..."
if [ -n "$DISPLAY" ]; then
    echo -e "    ${GREEN}[OK] Menjalankan antarmuka GUI Host Manager di desktop...${NC}"
    cd "$SCRIPT_DIR"
    nohup python3 digikeyboard_gui.py >/dev/null 2>&1 &
else
    if ! python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/version', timeout=1)" 2>/dev/null; then
        echo -e "    ${GREEN}[OK] Menjalankan DigiSmartDeck Server background...${NC}"
        cd "$SCRIPT_DIR"
        python3 server.py
    fi
fi

echo -e "\n${GREEN}[SUKSES] Instalasi DigiSmartDeck Host selesai.${NC}"
