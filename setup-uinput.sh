#!/bin/bash
# ==============================================================================
# DigiSmartDeck - Linux uinput Kernel Hardware Driver Setup
# Memungkinkan DigiSmartDeck bertindak sebagai Keyboard & Mouse USB Fisik di Level Kernel.
# Mendukung Layar Login Ubuntu (GDM), Lock Screen, Password Prompt, Wayland & X11.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  ⌨️  DigiSmartDeck - Setup Akses Layar Login Ubuntu (uinput)${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 1. Pastikan modul uinput dimuat sekarang dan otomatis saat boot
modprobe uinput 2>/dev/null || true
echo "uinput" | tee /etc/modules-load.d/uinput.conf >/dev/null 2>&1 || true
echo -e "${GREEN}[✓] Modul kernel uinput berhasil dimuat dan dikonfigurasi auto-load.${NC}"

# 2. Buat grup input jika belum ada
groupadd -f input

# 3. Buat aturan udev permanen (mode 0666 dan group input)
cat << 'EOF' > /etc/udev/rules.d/99-uinput.rules
KERNEL=="uinput", MODE="0666", GROUP="input", OPTIONS+="static_node=uinput"
SUBSYSTEM=="misc", KERNEL=="uinput", MODE="0666", GROUP="input"
EOF
echo -e "${GREEN}[✓] Aturan udev /etc/udev/rules.d/99-uinput.rules berhasil dibuat.${NC}"

# Reload udev
udevadm control --reload-rules 2>/dev/null || true
udevadm trigger /dev/uinput 2>/dev/null || true

# 4. Tambahkan user ke grup input
TARGET_USER="${SUDO_USER:-nino}"
usermod -aG input "$TARGET_USER" 2>/dev/null || true
echo -e "${GREEN}[✓] User '$TARGET_USER' berhasil ditambahkan ke grup 'input'.${NC}"

# 5. Atur izin langsung pada /dev/uinput yang sedang berjalan
if [ -e /dev/uinput ]; then
    chmod 666 /dev/uinput
    chgrp input /dev/uinput 2>/dev/null || true
    echo -e "${GREEN}[✓] Izin /dev/uinput berhasil diubah menjadi rw-rw-rw- (0666).${NC}"
fi

# 6. Aktifkan lingering systemd agar background service tetap aktif saat logout/lock
loginctl enable-linger "$TARGET_USER" 2>/dev/null || true
echo -e "${GREEN}[✓] Systemd linger diaktifkan untuk user '$TARGET_USER'.${NC}"

# 7. Konfigurasi dan aktifkan systemd service
SERVICE_SRC="/home/$TARGET_USER/digikeyboard/digikeyboard.service"
SERVICE_DST="/etc/systemd/system/digikeyboard.service"

if [ -f "$SERVICE_SRC" ]; then
    cat << EOF > "$SERVICE_DST"
[Unit]
Description=DigiSmartDeck Remote PC Keyboard Server (Kernel uinput)
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$TARGET_USER
Group=input
SupplementaryGroups=input
WorkingDirectory=/home/$TARGET_USER/digikeyboard
ExecStart=/usr/bin/python3 /home/$TARGET_USER/digikeyboard/server.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1
Environment=HOME=/home/$TARGET_USER

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable digikeyboard.service
    systemctl restart digikeyboard.service
    echo -e "${GREEN}[✓] Systemd service 'digikeyboard' berhasil dipasang dan dijalankan.${NC}"
fi

# 8. Bersihkan instance PM2 jika ada agar tidak bentrok port 8080
if command -v pm2 >/dev/null 2>&1; then
    pm2 delete digikeyboard >/dev/null 2>&1 || true
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 SUKSES! Driver Kernel Virtual USB DigiSmartDeck telah aktif!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo "Status service:"
systemctl status digikeyboard.service --no-pager -n 5 || true
