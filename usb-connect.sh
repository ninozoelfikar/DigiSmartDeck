#!/usr/bin/env bash
# DigiKeyboard 1-Click USB Connection Helper
# Otomatis mengaktifkan port reverse forwarding & membuka DigiKeyboard di HP via kabel USB
set -e

PORT=${1:-8080}
echo "============================================================"
echo "  🔌 DigiKeyboard USB Connection Helper (<1ms Latency)"
echo "============================================================"

if ! command -v adb &> /dev/null; then
    echo "[❌] ADB tidak ditemukan di komputer ini."
    echo "     Install dengan: sudo apt install adb (Linux) atau unduh platform-tools."
    exit 1
fi

echo "[*] Memeriksa koneksi perangkat Android via kabel USB..."
DEVICES=$(adb devices | grep -w "device" | awk '{print $1}')

if [ -z "$DEVICES" ]; then
    echo "[⚠️] Belum ada perangkat Android dengan USB Debugging terdeteksi."
    echo ""
    echo "  Petunjuk singkat:"
    echo "  1. Colokkan kabel USB dari HP ke PC."
    echo "  2. Pastikan 'USB Debugging' di Opsi Pengembang HP sudah aktif."
    echo "  3. Centang 'Selalu izinkan dari komputer ini' jika muncul pop-up di HP."
    echo ""
    echo "  Tips alternatif (Tanpa Debugging):"
    echo "  Aktifkan 'Penambatan USB' di Pengaturan HP -> Hotspot & Tethering."
    exit 1
fi

for DEV in $DEVICES; do
    echo "[✓] Mengaktifkan port reverse forwarding untuk perangkat: $DEV"
    adb -s "$DEV" reverse "tcp:$PORT" "tcp:$PORT"
    echo "[🚀] Membuka DigiKeyboard di Google Chrome HP..."
    adb -s "$DEV" shell am start -a android.intent.action.VIEW -d "http://localhost:$PORT" > /dev/null 2>&1 || true
done

echo "============================================================"
echo "[🎉] BERHASIL! DigiKeyboard terhubung via USB di HP: http://localhost:$PORT"
echo "     Latensi super rendah (<1ms) & bebas gangguan sinyal Wi-Fi."
echo "============================================================"
