#!/usr/bin/env python3
"""
DigiKeyboard PC Host Manager
Aplikasi Desktop Pusat Kendali untuk DigiKeyboard Host (Linux/X11)
"""

import os
import sys
import io
import json
import socket
import subprocess
import urllib.request
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon

import qrcode
from auth_manager import pairing_manager, license_manager

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, "assets", "icon.png")


def get_preferred_ip():
    """Mengambil IP jaringan lokal terbaik (prioritas Wi-Fi/Ethernet fisik)"""
    candidates = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        main_ip = s.getsockname()[0]
        s.close()
        candidates.append(main_ip)
    except Exception:
        pass

    try:
        out = subprocess.check_output(['hostname', '-I'], universal_newlines=True).strip()
        for ip in out.split():
            if ip not in candidates and not ip.startswith('127.'):
                candidates.append(ip)
    except Exception:
        pass

    # Urutkan prioritas: 192.168.8.x (Wi-Fi router pengguna), 192.168.x.x, 10.x.x.x
    # Hindari docker / virbr (172.17., 172.18., 172.16., 192.168.122.)
    def ip_score(ip):
        if ip.startswith('192.168.8.'):
            return 100
        if ip.startswith('192.168.') and not ip.startswith('192.168.122.'):
            return 80
        if ip.startswith('10.'):
            return 60
        if ip.startswith('172.') or ip.startswith('192.168.122.'):
            return 10
        return 20

    candidates.sort(key=ip_score, reverse=True)
    return candidates[0] if candidates else '127.0.0.1'


class DigiKeyboardGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DigiKeyboard - Host Control Center")
        self.resize(860, 640)
        self.setMinimumSize(800, 580)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.apply_theme()
        self.init_ui()

        # Timer untuk pembaruan status berkala (setiap 2 detik)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(2500)

        self.refresh_status()

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#centralWidget {
                background-color: #0f1115;
                color: #e6edf3;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            QFrame.card {
                background-color: #181b21;
                border: 1px solid #30363d;
                border-radius: 10px;
                padding: 16px;
            }
            QLabel.card-title {
                font-size: 13px;
                font-weight: 700;
                color: #ff6b00;
                letter-spacing: 0.5px;
            }
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #30363d;
                color: #ffffff;
                border-color: #8b949e;
            }
            QPushButton.primary {
                background-color: #ff6b00;
                color: #ffffff;
                border: none;
            }
            QPushButton.primary:hover {
                background-color: #e05e00;
            }
            QTableWidget {
                background-color: #12141a;
                border: 1px solid #30363d;
                border-radius: 6px;
                gridline-color: #21262d;
                color: #e6edf3;
            }
            QHeaderView::section {
                background-color: #181b21;
                color: #8b949e;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #21262d;
            }
        """)

    def init_ui(self):
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Header Bar
        header = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("DIGIKEYBOARD HOST CONTROL")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        subtitle = QLabel("Pusat Otorisasi Perangkat & Layanan Remote PC")
        subtitle.setStyleSheet("font-size: 12px; color: #8b949e;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header.addLayout(header_text)
        header.addStretch()

        self.lbl_server_badge = QLabel("MEMERIKSA...")
        self.lbl_server_badge.setStyleSheet(
            "background-color: #238636; color: #ffffff; font-weight: bold; padding: 6px 14px; border-radius: 12px; font-size: 11px;"
        )
        header.addWidget(self.lbl_server_badge)
        main_layout.addLayout(header)

        # Top Row: Pairing PIN & QR Code
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        # Card 1: Pairing PIN
        card_pin = QFrame()
        card_pin.setStyleSheet("QFrame { background-color: #181b21; border: 1px solid #30363d; border-radius: 10px; }")
        pin_layout = QVBoxLayout(card_pin)
        pin_layout.setContentsMargins(16, 14, 16, 14)
        pin_layout.setSpacing(8)

        lbl_pin_title = QLabel("KODE PIN PAIRING PERANGKAT")
        lbl_pin_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #ff6b00;")
        pin_desc = QLabel("Masukkan 6 digit angka ini pada ponsel saat pertama kali menyambung:")
        pin_desc.setWordWrap(True)
        pin_desc.setStyleSheet("color: #8b949e; font-size: 11px;")

        self.lbl_pin = QLabel("------")
        self.lbl_pin.setAlignment(Qt.AlignCenter)
        self.lbl_pin.setFixedHeight(52)
        self.lbl_pin.setStyleSheet(
            "font-family: monospace; font-size: 26px; font-weight: 800; color: #58a6ff; "
            "background-color: #0f1115; border: 1px solid #30363d; border-radius: 8px; letter-spacing: 6px;"
        )

        pin_btn_row = QHBoxLayout()
        btn_copy_pin = QPushButton("Salin PIN")
        btn_copy_pin.clicked.connect(self.copy_pin)
        btn_regen_pin = QPushButton("Acak Ulang PIN")
        btn_regen_pin.clicked.connect(self.regen_pin)
        pin_btn_row.addWidget(btn_copy_pin)
        pin_btn_row.addWidget(btn_regen_pin)

        pin_layout.addWidget(lbl_pin_title)
        pin_layout.addWidget(pin_desc)
        pin_layout.addWidget(self.lbl_pin)
        pin_layout.addLayout(pin_btn_row)

        top_row.addWidget(card_pin, 1)

        # Card 2: QR Code & Connection Address
        card_conn = QFrame()
        card_conn.setStyleSheet("QFrame { background-color: #181b21; border: 1px solid #30363d; border-radius: 10px; }")
        conn_layout = QHBoxLayout(card_conn)
        conn_layout.setContentsMargins(16, 14, 16, 14)
        conn_layout.setSpacing(14)

        self.lbl_qr = QLabel()
        self.lbl_qr.setFixedSize(120, 120)
        self.lbl_qr.setAlignment(Qt.AlignCenter)
        self.lbl_qr.setStyleSheet("background-color: #ffffff; border-radius: 6px; padding: 2px;")
        conn_layout.addWidget(self.lbl_qr)

        conn_info = QVBoxLayout()
        conn_info.setSpacing(6)
        lbl_conn_title = QLabel("ALAMAT KONEKSI PONSEL")
        lbl_conn_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #ff6b00;")
        conn_desc = QLabel("Scan QR di samping atau buka tautan di browser HP:")
        conn_desc.setStyleSheet("color: #8b949e; font-size: 11px;")

        self.lbl_url = QLabel("http://localhost:8080")
        self.lbl_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_url.setStyleSheet("font-family: monospace; font-size: 13px; font-weight: bold; color: #3fb950;")

        btn_copy_url = QPushButton("Salin URL")
        btn_copy_url.clicked.connect(self.copy_url)

        conn_info.addWidget(lbl_conn_title)
        conn_info.addWidget(conn_desc)
        conn_info.addWidget(self.lbl_url)
        conn_info.addWidget(btn_copy_url)
        conn_layout.addLayout(conn_info)

        top_row.addWidget(card_conn, 1)
        main_layout.addLayout(top_row)

        # Middle: Paired Devices List
        card_devices = QFrame()
        card_devices.setStyleSheet("QFrame { background-color: #181b21; border: 1px solid #30363d; border-radius: 10px; }")
        dev_layout = QVBoxLayout(card_devices)
        dev_layout.setContentsMargins(16, 14, 16, 14)
        dev_layout.setSpacing(8)

        dev_header = QHBoxLayout()
        lbl_dev_title = QLabel("DAFTAR PERANGKAT TEROTORISASI (PAIRED DEVICES)")
        lbl_dev_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #ff6b00;")
        dev_header.addWidget(lbl_dev_title)
        dev_header.addStretch()
        self.lbl_dev_count = QLabel("0 Perangkat")
        self.lbl_dev_count.setStyleSheet("color: #8b949e; font-size: 12px;")
        dev_header.addWidget(self.lbl_dev_count)
        dev_layout.addLayout(dev_header)

        self.table_devices = QTableWidget(0, 4)
        self.table_devices.setHorizontalHeaderLabels(["Nama Perangkat", "Alamat IP", "Waktu Terhubung", "Tindakan"])
        self.table_devices.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_devices.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_devices.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_devices.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_devices.setSelectionMode(QTableWidget.NoSelection)
        self.table_devices.setMinimumHeight(120)
        dev_layout.addWidget(self.table_devices)

        main_layout.addWidget(card_devices)

        # Bottom Row: License Card
        card_lic = QFrame()
        card_lic.setStyleSheet("QFrame { background-color: #181b21; border: 1px solid #30363d; border-radius: 10px; }")
        lic_layout = QHBoxLayout(card_lic)
        lic_layout.setContentsMargins(16, 12, 16, 12)

        lic_info = QVBoxLayout()
        lic_info.setSpacing(4)
        lbl_lic_title = QLabel("STATUS LISENSI SAAS")
        lbl_lic_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #ff6b00;")
        self.lbl_lic_desc = QLabel("Memuat status lisensi...")
        self.lbl_lic_desc.setStyleSheet("font-size: 12px; color: #e6edf3;")
        lic_info.addWidget(lbl_lic_title)
        lic_info.addWidget(self.lbl_lic_desc)
        lic_layout.addLayout(lic_info)
        lic_layout.addStretch()

        btn_activate = QPushButton("Aktivasi Kunci Lisensi")
        btn_activate.clicked.connect(self.activate_license_dialog)
        lic_layout.addWidget(btn_activate)

        main_layout.addWidget(card_lic)

        # Action Buttons Footer
        footer = QHBoxLayout()
        btn_open_browser = QPushButton("Buka DigiKeyboard di Browser")
        btn_open_browser.setStyleSheet("background-color: #ff6b00; color: #ffffff; font-weight: bold; padding: 9px 16px; border: none; border-radius: 6px;")
        btn_open_browser.clicked.connect(self.open_in_browser)

        btn_restart = QPushButton("Restart Layanan Server")
        btn_restart.clicked.connect(self.restart_service)

        footer.addWidget(btn_open_browser)
        footer.addWidget(btn_restart)
        footer.addStretch()

        lbl_version = QLabel("DigiKeyboard v0.9.35 (Linux Host)")
        lbl_version.setStyleSheet("color: #484f58; font-size: 11px;")
        footer.addWidget(lbl_version)

        main_layout.addLayout(footer)

    def refresh_status(self):
        # 1. Update PIN
        pin = pairing_manager.get_or_create_pin()
        formatted_pin = f"{pin[:3]} {pin[3:]}" if len(pin) == 6 else pin
        self.lbl_pin.setText(formatted_pin)

        # 2. Update Connection URL & QR
        target_ip = get_preferred_ip()
        url = f"http://{target_ip}:8080"
        self.lbl_url.setText(url)
        self.generate_qr(url)

        # 3. Check Server Running
        is_running = self.check_server_online()
        if is_running:
            self.lbl_server_badge.setText("SERVER AKTIF (PORT 8080)")
            self.lbl_server_badge.setStyleSheet(
                "background-color: #238636; color: #ffffff; font-weight: bold; padding: 6px 14px; border-radius: 12px; font-size: 11px;"
            )
        else:
            self.lbl_server_badge.setText("SERVER TERHENTI")
            self.lbl_server_badge.setStyleSheet(
                "background-color: #da3633; color: #ffffff; font-weight: bold; padding: 6px 14px; border-radius: 12px; font-size: 11px;"
            )

        # 4. Update Paired Devices
        devices = pairing_manager.get_paired_list()
        self.lbl_dev_count.setText(f"{len(devices)} Perangkat")
        self.table_devices.setRowCount(len(devices))
        for row, dev in enumerate(devices):
            self.table_devices.setItem(row, 0, QTableWidgetItem(dev.get("name", "Unknown")))
            self.table_devices.setItem(row, 1, QTableWidgetItem(dev.get("ip", "-")))
            self.table_devices.setItem(row, 2, QTableWidgetItem(dev.get("paired_at", "-")))

            btn_del = QPushButton("Putuskan")
            btn_del.setStyleSheet("padding: 4px 8px; font-size: 11px; background-color: #da3633; color: #ffffff; border: none; border-radius: 4px;")
            dev_id = dev.get("device_id")
            btn_del.clicked.connect(lambda ch, d=dev_id: self.unpair_device(d))
            self.table_devices.setCellWidget(row, 3, btn_del)

        # 5. Update License Info
        lic = license_manager.get_info()
        tier_name = lic.get("plan_name", "Free Trial")
        days = lic.get("days_left", 0)
        status_str = f"Paket: {tier_name} | Status: Aktif"
        if days >= 0:
            status_str += f" | Sisa Waktu: {days} Hari"
        self.lbl_lic_desc.setText(status_str)

    def generate_qr(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        img.save(bio, format="PNG")
        pix = QPixmap()
        pix.loadFromData(bio.getvalue())
        self.lbl_qr.setPixmap(pix.scaled(116, 116, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def check_server_online(self):
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/api/pairing/pin", headers={"User-Agent": "DigiGUI"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                return resp.status == 200
        except Exception:
            return False

    def copy_pin(self):
        pin = pairing_manager.get_or_create_pin()
        QApplication.clipboard().setText(pin)
        QMessageBox.information(self, "Tersalin", f"Kode PIN {pin} telah disalin ke papan klip.")

    def regen_pin(self):
        new_pin = pairing_manager.generate_pin()
        self.refresh_status()
        QMessageBox.information(self, "PIN Diperbarui", f"Kode PIN baru: {new_pin}")

    def copy_url(self):
        url = self.lbl_url.text()
        QApplication.clipboard().setText(url)
        QMessageBox.information(self, "Tersalin", f"URL {url} telah disalin ke papan klip.")

    def open_in_browser(self):
        url = self.lbl_url.text()
        subprocess.Popen(["xdg-open", url])

    def restart_service(self):
        subprocess.run(["pkill", "-f", "/home/nino/digikeyboard/server.py"])
        QTimer.singleShot(1500, self.refresh_status)
        QMessageBox.information(self, "Restart Layanan", "Perintah restart server telah dikirim ke systemd.")

    def unpair_device(self, dev_id):
        if not dev_id:
            return
        pairing_manager.unpair_device(dev_id)
        self.refresh_status()

    def activate_license_dialog(self):
        key, ok = QInputDialog.getText(
            self, "Aktivasi Lisensi", "Masukkan Kunci Lisensi DigiKeyboard (contoh: DIGI-LIFE-XXXX-XXXX):"
        )
        if ok and key:
            key = key.strip()
            success, msg = license_manager.activate_key(key)
            if success:
                QMessageBox.information(self, "Aktivasi Sukses", msg)
                self.refresh_status()
            else:
                QMessageBox.warning(self, "Aktivasi Gagal", msg)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DigiKeyboard Host")
    gui = DigiKeyboardGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
