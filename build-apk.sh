#!/usr/bin/env bash
# ==============================================================================
# DigiKeyboard - Android APK Builder
# Mengompilasi aplikasi Android mandiri (True Immersive Fullscreen, 0% Chrome Pop-up)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/android"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  📱  DigiKeyboard - Android APK Builder${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Konfigurasi environment Android SDK & Java jika belum ada di PATH
if [ -z "$JAVA_HOME" ]; then
    if [ -d "/home/nino/.local/share/jdk" ]; then
        export JAVA_HOME="/home/nino/.local/share/jdk"
        export PATH="$JAVA_HOME/bin:$PATH"
    elif [ -d "/home/nino/.antigravity/extensions/redhat.java-1.54.0-linux-x64/jre/21.0.10-linux-x86_64" ]; then
        export JAVA_HOME="/home/nino/.antigravity/extensions/redhat.java-1.54.0-linux-x64/jre/21.0.10-linux-x86_64"
        export PATH="$JAVA_HOME/bin:$PATH"
    fi
fi

if [ -z "$ANDROID_HOME" ] && [ -d "/home/nino/Android/sdk" ]; then
    export ANDROID_HOME="/home/nino/Android/sdk"
fi

echo -e "${GREEN}[✓] Memulai proses kompilasi APK via Gradle Wrapper...${NC}"
./gradlew assembleDebug

mkdir -p "$SCRIPT_DIR/dist"
mkdir -p "$SCRIPT_DIR/static"
cp app/build/outputs/apk/debug/app-debug.apk "$SCRIPT_DIR/dist/DigiKeyboard.apk"
cp app/build/outputs/apk/debug/app-debug.apk "$SCRIPT_DIR/static/DigiKeyboard.apk"

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}[✓] BERHASIL! File APK Android telah dibuat:${NC}"
echo -e "    File APK: ${BLUE}${SCRIPT_DIR}/dist/DigiKeyboard.apk${NC}"
echo -e "    Ukuran:   $(du -h "$SCRIPT_DIR/dist/DigiKeyboard.apk" | cut -f1)"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Cara Pasang di HP:"
echo "1. Kirim file DigiKeyboard.apk ke HP via WhatsApp, Bluetooth, atau kabel data."
echo "2. Atau langsung buka di HP: http://<IP-PC>:8080/static/DigiKeyboard.apk"
echo "3. Pasang (install) dan nikmati keyboard remote 100% bebas dari segala pop-up Chrome!"
echo ""
