#!/bin/bash
# ==============================================================================
# DigiKeyboard - Linux uinput Kernel Hardware Driver Setup
# Memungkinkan DigiKeyboard bertindak sebagai Keyboard & Mouse USB Fisik di Level Kernel.
# Mendukung Layar Login Ubuntu (GDM), Lock Screen, Password Prompt, Wayland & X11.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  ⌨️  DigiKeyboard - Setup Akses Layar Login Ubuntu (uinput)${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}Penjelasan:${NC}"
echo "Layar Login dan Lock Screen Ubuntu (GDM) secara bawaan memblokir simulasi"
echo "keyboard software (XTest) demi alasan keamanan. Agar DigiKeyboard dapat"
echo "mengetik password di layar login, DigiKeyboard harus didaftarkan sebagai"
echo "Keyboard USB Fisik di level kernel Linux menggunakan modul 'uinput'."
echo ""
echo "Skrip ini membutuhkan akses sudo untuk:"
echo " 1. Membuat aturan udev /etc/udev/rules.d/99-uinput.rules"
echo " 2. Menambahkan user '$USER' ke grup 'input'"
echo " 3. Memberikan izin baca/tulis ke /dev/uinput"
echo " 4. Mengaktifkan lingering (agar service tetap jalan sebelum login)"
echo ""

# 1. Pastikan modul uinput aktif
sudo modprobe uinput 2>/dev/null || true

# 2. Buat grup input jika belum ada
sudo groupadd -f input

# 3. Tambahkan aturan udev
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null
echo -e "${GREEN}[✓] Aturan udev /etc/udev/rules.d/99-uinput.rules berhasil dibuat.${NC}"

# 4. Tambahkan user ke grup input
sudo usermod -aG input "$USER"
echo -e "${GREEN}[✓] User '$USER' berhasil ditambahkan ke grup 'input'.${NC}"

# 5. Atur izin langsung pada /dev/uinput yang sedang berjalan
if [ -e /dev/uinput ]; then
    sudo chmod 660 /dev/uinput
    sudo chgrp input /dev/uinput
    # Izin rw untuk user saat ini di sesi ini
    sudo chmod 666 /dev/uinput
    echo -e "${GREEN}[✓] Izin /dev/uinput berhasil dikonfigurasi.${NC}"
fi

# 6. Aktifkan lingering systemd agar background service tetap aktif saat logout/lock
loginctl enable-linger "$USER" 2>/dev/null || true
echo -e "${GREEN}[✓] Systemd linger diaktifkan untuk user '$USER'.${NC}"

# 7. Restart PM2 jika ada
if command -v pm2 >/dev/null 2>&1; then
    if pm2 describe digikeyboard >/dev/null 2>&1; then
        pm2 restart digikeyboard >/dev/null 2>&1 || true
        echo -e "${GREEN}[✓] Service PM2 'digikeyboard' berhasil direstart.${NC}"
    fi
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 SUKSES! Driver Kernel Virtual USB DigiKeyboard telah aktif!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo "Sekarang DigiKeyboard dapat mengisi password pada:"
echo " - Layar Login Pengguna Ubuntu (GDM)"
echo " - Layar Kunci (Lock Screen)"
echo " - Sesi Wayland & X11"
echo " - Terminal sudo / root password"
echo ""
echo "Catatan: Agar keanggotaan grup 'input' permanen di semua terminal,"
echo "Anda disarankan melakukan Logout & Login kembali sekali saja."
echo "============================================================"
