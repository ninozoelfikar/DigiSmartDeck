#!/usr/bin/env bash
# ==============================================================================
# DigiSmartDeck - Android APK Builder
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
echo -e "${BLUE}  DigiSmartDeck - Android APK Builder${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Konfigurasi environment Android SDK & Java jika belum ada di PATH
if [ -z "$JAVA_HOME" ]; then
    JDK_FOUND=$(find "$HOME/.local/share" -maxdepth 1 -type d -name "jdk*" 2>/dev/null | head -n 1)
    if [ -n "$JDK_FOUND" ]; then
        export JAVA_HOME="$JDK_FOUND"
        export PATH="$JAVA_HOME/bin:$PATH"
    elif [ -d "$HOME/.antigravity/extensions/redhat.java-1.54.0-linux-x64/jre/21.0.10-linux-x86_64" ]; then
        export JAVA_HOME="$HOME/.antigravity/extensions/redhat.java-1.54.0-linux-x64/jre/21.0.10-linux-x86_64"
        export PATH="$JAVA_HOME/bin:$PATH"
    fi
fi

if [ -z "$ANDROID_HOME" ] && [ -d "$HOME/Android/sdk" ]; then
    export ANDROID_HOME="$HOME/Android/sdk"
fi

echo -e "${GREEN}[OK] Memulai proses kompilasi APK via Gradle Wrapper...${NC}"
./gradlew assembleDebug

APP_VER="1.18.4"
if [ -f "$SCRIPT_DIR/VERSION" ]; then
    APP_VER=$(tr -d '[:space:]' < "$SCRIPT_DIR/VERSION")
fi
APK_VER_NAME="DigiSmartDeck-v${APP_VER}.apk"

mkdir -p "$SCRIPT_DIR/dist"
mkdir -p "$SCRIPT_DIR/static"
cp app/build/outputs/apk/debug/app-debug.apk "$SCRIPT_DIR/dist/${APK_VER_NAME}"
cp app/build/outputs/apk/debug/app-debug.apk "$SCRIPT_DIR/dist/DigiSmartDeck.apk"
cp app/build/outputs/apk/debug/app-debug.apk "$SCRIPT_DIR/static/${APK_VER_NAME}"
cp app/build/outputs/apk/debug/app-debug.apk "$SCRIPT_DIR/static/DigiSmartDeck.apk"

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}[OK] BERHASIL! File APK Android telah dibuat:${NC}"
echo -e "    File APK Versi: ${BLUE}${SCRIPT_DIR}/dist/${APK_VER_NAME}${NC}"
echo -e "    File APK Default: ${BLUE}${SCRIPT_DIR}/dist/DigiSmartDeck.apk${NC}"
echo -e "    Ukuran:          $(du -h "$SCRIPT_DIR/dist/${APK_VER_NAME}" | cut -f1)"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Cara Pasang di HP:"
echo "1. Kirim file ${APK_VER_NAME} ke HP via WhatsApp, Bluetooth, atau kabel data."
echo "2. Atau langsung buka di HP: http://<IP-PC>:8080/static/${APK_VER_NAME}"
echo "3. Pasang (install) dan nikmati keyboard remote 100% bebas dari segala pop-up Chrome!"
echo ""
