#!/usr/bin/env python3
"""
DigiSmartDeck PC Host Manager & Setup Wizard
Aplikasi Desktop Pusat Kendali & Installer untuk DigiSmartDeck Host (Linux/X11)
Desain visual selaras penuh dengan antarmuka Web Client DigiSmartDeck.
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
    QHeaderView, QMessageBox, QLineEdit, QStackedWidget,
    QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon

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


class DigiSmartDeckGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DigiSmartDeck Host Manager")
        self.resize(920, 680)
        self.setMinimumSize(860, 620)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.apply_theme()
        self.init_ui()

        # Polling status berkala (setiap 2 detik)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(2000)

        self.refresh_status()

    def apply_theme(self):
        """Menerapkan stylesheet QSS modern yang identik dengan Web Client DigiSmartDeck"""
        self.setStyleSheet("""
            QMainWindow, QWidget#centralWidget {
                background-color: #0d1117;
                color: #f0f6fc;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            QLabel {
                color: #f0f6fc;
            }
            /* Header Deck */
            QFrame#topDeck {
                background-color: #161b22;
                border-bottom: 1px solid #30363d;
                padding: 10px 16px;
            }
            /* Navigation Chips Bar */
            QFrame#navDeck {
                background-color: #161b22;
                border-bottom: 1px solid #30363d;
                padding: 6px 16px;
            }
            QPushButton.nav-chip {
                background-color: #21262d;
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 7px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton.nav-chip:hover {
                background-color: #30363d;
                color: #f0f6fc;
                border-color: #58a6ff;
            }
            QPushButton.nav-chip.active {
                background-color: #1f6feb;
                color: #ffffff;
                border: 1px solid #58a6ff;
                font-weight: 700;
            }
            /* Cards */
            QFrame.card-panel {
                background-color: #1c2128;
                border: 1px solid #30363d;
                border-radius: 10px;
                padding: 16px;
            }
            QLabel.card-header-title {
                font-size: 13px;
                font-weight: 800;
                color: #ff6b00;
                letter-spacing: 0.5px;
            }
            QLabel.card-desc {
                font-size: 11px;
                color: #8b949e;
                line-height: 1.4;
            }
            /* Keycap PIN Box */
            QLabel.pin-keycap {
                background-color: #12141a;
                border: 2px solid #30363d;
                border-radius: 8px;
                font-family: monospace;
                font-size: 28px;
                font-weight: 800;
                color: #58a6ff;
                min-width: 48px;
                max-width: 52px;
                min-height: 54px;
                max-height: 58px;
                qproperty-alignment: AlignCenter;
            }
            /* General Buttons */
            QPushButton.btn-primary {
                background-color: #ff6b00;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton.btn-primary:hover {
                background-color: #e05e00;
            }
            QPushButton.btn-secondary {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton.btn-secondary:hover {
                background-color: #30363d;
                color: #ffffff;
                border-color: #8b949e;
            }
            QPushButton.btn-danger {
                background-color: #da3633;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton.btn-danger:hover {
                background-color: #b62324;
            }
            /* Table */
            QTableWidget {
                background-color: #12141a;
                border: 1px solid #30363d;
                border-radius: 8px;
                gridline-color: #21262d;
                color: #f0f6fc;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #161b22;
                color: #8b949e;
                padding: 8px;
                font-weight: 700;
                border: 1px solid #21262d;
            }
            /* Input line */
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f0f6fc;
                font-family: monospace;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
            /* Log terminal viewer */
            QTextEdit#logViewer {
                background-color: #090d13;
                border: 1px solid #30363d;
                border-radius: 8px;
                color: #7ee787;
                font-family: monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)

    def init_ui(self):
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 1. Top Deck Header ──
        top_deck = QFrame()
        top_deck.setObjectName("topDeck")
        top_layout = QHBoxLayout(top_deck)
        top_layout.setContentsMargins(16, 10, 16, 10)

        if os.path.exists(ICON_PATH):
            logo_lbl = QLabel()
            pix = QPixmap(ICON_PATH).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            top_layout.addWidget(logo_lbl)
            top_layout.addSpacing(10)

        logo_title_layout = QVBoxLayout()
        logo_title_layout.setSpacing(2)
        app_title = QLabel("DIGISMARTDECK HOST")
        app_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #ffffff; letter-spacing: 0.8px;")
        app_sub = QLabel("Pusat Kendali Otorisasi & Layanan Input PC")
        app_sub.setStyleSheet("font-size: 11px; color: #8b949e;")
        logo_title_layout.addWidget(app_title)
        logo_title_layout.addWidget(app_sub)
        top_layout.addLayout(logo_title_layout)

        top_layout.addStretch()

        # Status Chips
        self.lbl_server_status = QLabel("SERVER AKTIF")
        self.lbl_server_status.setStyleSheet(
            "background-color: #238636; color: #ffffff; font-weight: 700; "
            "padding: 5px 12px; border-radius: 12px; font-size: 11px;"
        )
        top_layout.addWidget(self.lbl_server_status)

        latency_badge = QLabel("USB: <1ms | Wi-Fi LAN")
        latency_badge.setStyleSheet(
            "background-color: #1f242c; color: #58a6ff; border: 1px solid #30363d; "
            "padding: 5px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;"
        )
        top_layout.addWidget(latency_badge)

        btn_open_web_top = QPushButton("Buka Web Client")
        btn_open_web_top.setProperty("class", "btn-primary")
        btn_open_web_top.clicked.connect(self.open_in_browser)
        top_layout.addWidget(btn_open_web_top)

        root_layout.addWidget(top_deck)

        # ── 2. Navigation Deck Chips ──
        nav_deck = QFrame()
        nav_deck.setObjectName("navDeck")
        nav_layout = QHBoxLayout(nav_deck)
        nav_layout.setContentsMargins(16, 6, 16, 6)
        nav_layout.setSpacing(8)

        self.nav_buttons = []
        tab_names = [
            ("Pusat Kendali", 0),
            ("Perangkat Terdaftar", 1),
            ("Lisensi SaaS", 2),
            ("Wizard Setup", 3)
        ]

        for title, idx in tab_names:
            btn = QPushButton(title)
            btn.setProperty("class", "nav-chip")
            btn.setCheckable(True)
            btn.clicked.connect(lambda ch, i=idx: self.switch_tab(i))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()
        root_layout.addWidget(nav_deck)

        # ── 3. Content Pages (QStackedWidget) ──
        self.stack = QStackedWidget()
        self.page_pairing = self.create_page_pairing()
        self.page_devices = self.create_page_devices()
        self.page_license = self.create_page_license()
        self.page_wizard = self.create_page_wizard()

        self.stack.addWidget(self.page_pairing)
        self.stack.addWidget(self.page_devices)
        self.stack.addWidget(self.page_license)
        self.stack.addWidget(self.page_wizard)

        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.addWidget(self.stack)
        root_layout.addWidget(content_container, 1)

        # Footer Status
        footer = QFrame()
        footer.setStyleSheet("background-color: #161b22; border-top: 1px solid #30363d; padding: 6px 16px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 4, 16, 4)

        self.lbl_footer_info = QLabel("Port: 8080 | Status Layanan: Aktif")
        self.lbl_footer_info.setStyleSheet("color: #8b949e; font-size: 11px;")
        footer_layout.addWidget(self.lbl_footer_info)

        footer_layout.addStretch()

        ver_lbl = QLabel("DigiSmartDeck v0.9.38 (Linux Host Edition)")
        ver_lbl.setStyleSheet("color: #484f58; font-size: 11px;")
        footer_layout.addWidget(ver_lbl)

        root_layout.addWidget(footer)

        self.switch_tab(0)

    def switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            if i == idx:
                btn.setChecked(True)
                btn.setStyleSheet("background-color: #1f6feb; color: #ffffff; border: 1px solid #58a6ff; font-weight: 700;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("background-color: #21262d; color: #8b949e; border: 1px solid #30363d; font-weight: 600;")
        if idx == 3:
            self.update_log_viewer()

    # ── Page 1: Pusat Kendali & Pairing ──
    def create_page_pairing(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        top_cards = QHBoxLayout()
        top_cards.setSpacing(14)

        # Card A: Segmented 6-Digit PIN Display
        card_pin = QFrame()
        card_pin.setProperty("class", "card-panel")
        pin_layout = QVBoxLayout(card_pin)
        pin_layout.setContentsMargins(14, 12, 14, 12)
        pin_layout.setSpacing(6)

        pin_title = QLabel("KODE PIN OTORISASI PERANGKAT")
        pin_title.setProperty("class", "card-header-title")
        pin_desc = QLabel("Masukkan 6 digit angka di bawah pada antarmuka ponsel Anda:")
        pin_desc.setProperty("class", "card-desc")

        pin_layout.addWidget(pin_title)
        pin_layout.addWidget(pin_desc)

        # 6 Separate Keycap Boxes
        self.pin_keycaps = []
        keycaps_row = QHBoxLayout()
        keycaps_row.setSpacing(8)
        keycaps_row.setAlignment(Qt.AlignCenter)

        for _ in range(6):
            box = QLabel("-")
            box.setProperty("class", "pin-keycap")
            keycaps_row.addWidget(box)
            self.pin_keycaps.append(box)

        pin_layout.addLayout(keycaps_row)

        pin_note = QLabel("Perangkat otomatis terhubung begitu 6 digit PIN dimasukkan.")
        pin_note.setStyleSheet("font-size: 11px; color: #3fb950; font-weight: 600; padding: 2px 0;")
        pin_note.setAlignment(Qt.AlignCenter)
        pin_layout.addWidget(pin_note)

        pin_btn_row = QHBoxLayout()
        btn_copy_pin = QPushButton("Salin PIN")
        btn_copy_pin.setProperty("class", "btn-secondary")
        btn_copy_pin.clicked.connect(self.copy_pin)

        btn_regen_pin = QPushButton("Acak Ulang PIN")
        btn_regen_pin.setProperty("class", "btn-secondary")
        btn_regen_pin.clicked.connect(self.regen_pin)

        pin_btn_row.addWidget(btn_copy_pin)
        pin_btn_row.addWidget(btn_regen_pin)
        pin_layout.addLayout(pin_btn_row)

        top_cards.addWidget(card_pin, 1)

        # Card B: QR Code & IP Connection Scanner
        card_qr = QFrame()
        card_qr.setProperty("class", "card-panel")
        qr_layout = QHBoxLayout(card_qr)
        qr_layout.setContentsMargins(14, 12, 14, 12)
        qr_layout.setSpacing(12)

        self.lbl_qr_img = QLabel()
        self.lbl_qr_img.setFixedSize(116, 116)
        self.lbl_qr_img.setAlignment(Qt.AlignCenter)
        self.lbl_qr_img.setStyleSheet("background-color: #ffffff; border-radius: 6px; padding: 2px;")
        qr_layout.addWidget(self.lbl_qr_img)

        qr_info = QVBoxLayout()
        qr_info.setSpacing(6)
        qr_title = QLabel("SCAN & SAMBUNGKAN")
        qr_title.setProperty("class", "card-header-title")
        qr_desc = QLabel("Arahkan kamera ponsel ke QR code atau buka URL berikut:")
        qr_desc.setProperty("class", "card-desc")

        self.lbl_wifi_url = QLabel("http://localhost:8080")
        self.lbl_wifi_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_wifi_url.setStyleSheet("font-family: monospace; font-size: 13px; font-weight: 700; color: #3fb950;")

        btn_copy_url = QPushButton("Salin Tautan URL")
        btn_copy_url.setProperty("class", "btn-secondary")
        btn_copy_url.clicked.connect(self.copy_url)

        qr_info.addWidget(qr_title)
        qr_info.addWidget(qr_desc)
        qr_info.addWidget(self.lbl_wifi_url)
        qr_info.addWidget(btn_copy_url)
        qr_layout.addLayout(qr_info)

        top_cards.addWidget(card_qr, 1)
        layout.addLayout(top_cards)

        # Bottom Overview: Connection Methods Guide
        card_guide = QFrame()
        card_guide.setProperty("class", "card-panel")
        guide_layout = QVBoxLayout(card_guide)
        guide_layout.setContentsMargins(16, 14, 16, 14)
        guide_layout.setSpacing(8)

        guide_title = QLabel("METODE KONEKSI KE PC")
        guide_title.setProperty("class", "card-header-title")
        guide_layout.addWidget(guide_title)

        guide_cols = QHBoxLayout()
        guide_cols.setSpacing(16)

        col_wifi = QVBoxLayout()
        lbl_w_title = QLabel("1. Wi-Fi Jaringan Lokal (Nirkabel)")
        lbl_w_title.setStyleSheet("font-weight: 700; font-size: 12px; color: #f0f6fc;")
        lbl_w_desc = QLabel("Pastikan ponsel terhubung ke Wi-Fi yang sama dengan PC host. Buka browser ponsel ke alamat IP yang tertera.")
        lbl_w_desc.setStyleSheet("font-size: 11px; color: #8b949e;")
        lbl_w_desc.setWordWrap(True)
        col_wifi.addWidget(lbl_w_title)
        col_wifi.addWidget(lbl_w_desc)
        guide_cols.addLayout(col_wifi)

        col_usb = QVBoxLayout()
        lbl_u_title = QLabel("2. Kabel USB Tethering (<1ms Latency)")
        lbl_u_title.setStyleSheet("font-weight: 700; font-size: 12px; color: #f0f6fc;")
        lbl_u_desc = QLabel("Colokkan kabel USB dari ponsel ke PC, aktifkan USB Debugging atau Reverse Tethering. Latensi respons di bawah 1 milidetik.")
        lbl_u_desc.setStyleSheet("font-size: 11px; color: #8b949e;")
        lbl_u_desc.setWordWrap(True)
        col_usb.addWidget(lbl_u_title)
        col_usb.addWidget(lbl_u_desc)
        guide_cols.addLayout(col_usb)

        guide_layout.addLayout(guide_cols)
        layout.addWidget(card_guide)
        layout.addStretch()

        return page

    # ── Page 2: Perangkat Terdaftar ──
    def create_page_devices(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        card = QFrame()
        card.setProperty("class", "card-panel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        header_row = QHBoxLayout()
        title = QLabel("DAFTAR PERANGKAT TEROTORISASI (PAIRED CLIENTS)")
        title.setProperty("class", "card-header-title")
        header_row.addWidget(title)
        header_row.addStretch()

        self.lbl_paired_count = QLabel("0 Perangkat Terdaftar")
        self.lbl_paired_count.setStyleSheet("color: #8b949e; font-size: 12px;")
        header_row.addWidget(self.lbl_paired_count)

        btn_unpair_all = QPushButton("Putuskan Semua")
        btn_unpair_all.setProperty("class", "btn-secondary")
        btn_unpair_all.clicked.connect(self.unpair_all_devices)
        header_row.addWidget(btn_unpair_all)

        card_layout.addLayout(header_row)

        desc = QLabel("Perangkat di bawah ini telah diverifikasi dengan PIN 6-digit dan dapat langsung mengendalikan PC tanpa meminta PIN ulang.")
        desc.setProperty("class", "card-desc")
        card_layout.addWidget(desc)

        self.table_devs = QTableWidget(0, 4)
        self.table_devs.setHorizontalHeaderLabels(["Perangkat & Platform", "Alamat IP", "Waktu Pairing", "Tindakan"])
        self.table_devs.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_devs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_devs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_devs.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_devs.setSelectionMode(QTableWidget.NoSelection)
        self.table_devs.setMinimumHeight(240)
        card_layout.addWidget(self.table_devs)

        layout.addWidget(card)
        return page

    # ── Page 3: Lisensi & Akun SaaS ──
    def create_page_license(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Status Lisensi Aktif
        card_status = QFrame()
        card_status.setProperty("class", "card-panel")
        st_layout = QHBoxLayout(card_status)
        st_layout.setContentsMargins(16, 16, 16, 16)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        lic_header = QLabel("STATUS LISENSI SAAS HOST")
        lic_header.setProperty("class", "card-header-title")
        self.lbl_lic_status_text = QLabel("Memuat status...")
        self.lbl_lic_status_text.setStyleSheet("font-size: 14px; font-weight: 700; color: #f0f6fc;")
        self.lbl_lic_days = QLabel("Masa Berlaku: -")
        self.lbl_lic_days.setStyleSheet("font-size: 11px; color: #8b949e;")

        info_col.addWidget(lic_header)
        info_col.addWidget(self.lbl_lic_status_text)
        info_col.addWidget(self.lbl_lic_days)
        st_layout.addLayout(info_col)
        st_layout.addStretch()

        self.badge_lic_tier = QLabel("TRIAL")
        self.badge_lic_tier.setStyleSheet(
            "background-color: #ff6b00; color: #ffffff; font-weight: 800; "
            "padding: 6px 16px; border-radius: 6px; font-size: 12px;"
        )
        st_layout.addWidget(self.badge_lic_tier)
        layout.addWidget(card_status)

        # Pilihan Paket Komersial
        card_plans = QFrame()
        card_plans.setProperty("class", "card-panel")
        plans_layout = QVBoxLayout(card_plans)
        plans_layout.setContentsMargins(16, 16, 16, 16)
        plans_layout.setSpacing(10)

        plans_title = QLabel("PILIHAN PAKET KOMERSIAL")
        plans_title.setProperty("class", "card-header-title")
        plans_layout.addWidget(plans_title)

        plans_row = QHBoxLayout()
        plans_row.setSpacing(12)

        # Helper untuk kartu plan dengan kontras jelas
        def make_plan_card(title, sub, price, price_color, border_color="#30363d"):
            box = QFrame()
            box.setFixedHeight(84)
            box.setStyleSheet(f"QFrame {{ background-color: #12141a; border: 1px solid {border_color}; border-radius: 8px; }}")
            l = QVBoxLayout(box)
            l.setContentsMargins(14, 10, 14, 10)
            l.setSpacing(2)
            t = QLabel(title)
            t.setStyleSheet("QLabel { font-size: 13px; font-weight: 800; color: #ffffff; background: transparent; border: none; }")
            s = QLabel(sub)
            s.setStyleSheet("QLabel { font-size: 11px; color: #8b949e; background: transparent; border: none; }")
            p = QLabel(price)
            p.setStyleSheet(f"QLabel {{ font-size: 14px; font-weight: 800; color: {price_color}; background: transparent; border: none; }}")
            l.addWidget(t)
            l.addWidget(s)
            l.addWidget(p)
            return box

        plans_row.addWidget(make_plan_card("FREE TRIAL", "Akses Penuh 7 Hari", "Rp 0", "#3fb950"))
        plans_row.addWidget(make_plan_card("BERLANGGANAN", "Akses Penuh Bulanan", "Rp 15.000 / bln", "#58a6ff"))
        plans_row.addWidget(make_plan_card("LIFETIME PRO", "Seumur Hidup Tanpa Batas", "Rp 250.000", "#ff6b00", "#ff6b00"))

        plans_layout.addLayout(plans_row)
        layout.addWidget(card_plans)

        # Aktivasi Kunci Lisensi
        card_act = QFrame()
        card_act.setProperty("class", "card-panel")
        act_layout = QVBoxLayout(card_act)
        act_layout.setContentsMargins(16, 16, 16, 16)
        act_layout.setSpacing(8)

        act_title = QLabel("AKTIVASI KUNCI LISENSI")
        act_title.setProperty("class", "card-header-title")
        act_layout.addWidget(act_title)

        act_form = QHBoxLayout()
        self.txt_license_input = QLineEdit()
        self.txt_license_input.setPlaceholderText("DIGI-XXXX-XXXX-XXXX")
        act_form.addWidget(self.txt_license_input, 1)

        btn_submit_key = QPushButton("Aktifkan Kunci")
        btn_submit_key.setProperty("class", "btn-primary")
        btn_submit_key.clicked.connect(self.activate_key_submit)
        act_form.addWidget(btn_submit_key)

        act_layout.addLayout(act_form)
        layout.addWidget(card_act)
        layout.addStretch()

        return page

    # ── Page 4: Wizard Setup & Layanan (Installer) ──
    def create_page_wizard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        card_diag = QFrame()
        card_diag.setProperty("class", "card-panel")
        diag_layout = QVBoxLayout(card_diag)
        diag_layout.setContentsMargins(16, 16, 16, 16)
        diag_layout.setSpacing(10)

        diag_title = QLabel("KESIAPAN SISTEM HOST & KERNEL UINPUT")
        diag_title.setProperty("class", "card-header-title")
        diag_layout.addWidget(diag_title)

        diag_grid = QHBoxLayout()
        diag_grid.setSpacing(12)

        # Box 1: uinput status
        b_uinput = QFrame()
        b_uinput.setObjectName("boxUinput")
        b_uinput.setStyleSheet("QFrame#boxUinput { background-color: #12141a; border: 1px solid #30363d; border-radius: 8px; }")
        l_u = QVBoxLayout(b_uinput)
        l_u.setContentsMargins(14, 14, 14, 14)
        l_u.setSpacing(6)
        t_u = QLabel("Simulasi Kernel Hardware (/dev/uinput)")
        t_u.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.lbl_uinput_status = QLabel("MEMERIKSA...")
        self.lbl_uinput_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #3fb950; background: transparent; border: none;")
        l_u.addWidget(t_u)
        l_u.addWidget(self.lbl_uinput_status)
        diag_grid.addWidget(b_uinput)

        # Box 2: systemd status
        b_svc = QFrame()
        b_svc.setObjectName("boxSvc")
        b_svc.setStyleSheet("QFrame#boxSvc { background-color: #12141a; border: 1px solid #30363d; border-radius: 8px; }")
        l_s = QVBoxLayout(b_svc)
        l_s.setContentsMargins(14, 14, 14, 14)
        l_s.setSpacing(6)
        t_s = QLabel("Layanan Background (digikeyboard.service)")
        t_s.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.lbl_svc_status = QLabel("MEMERIKSA...")
        self.lbl_svc_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #3fb950; background: transparent; border: none;")
        l_s.addWidget(t_s)
        l_s.addWidget(self.lbl_svc_status)
        diag_grid.addWidget(b_svc)

        # Box 3: Smart Terminal Integration
        b_term = QFrame()
        b_term.setObjectName("boxTerm")
        b_term.setStyleSheet("QFrame#boxTerm { background-color: #12141a; border: 1px solid #30363d; border-radius: 8px; }")
        l_t = QVBoxLayout(b_term)
        l_t.setContentsMargins(14, 14, 14, 14)
        l_t.setSpacing(6)
        t_t = QLabel("Integrasi Smart Terminal Otomatis")
        t_t.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.lbl_smart_term_status = QLabel("MEMERIKSA...")
        self.lbl_smart_term_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #3fb950; background: transparent; border: none;")
        l_t.addWidget(t_t)
        l_t.addWidget(self.lbl_smart_term_status)
        diag_grid.addWidget(b_term)

        diag_layout.addLayout(diag_grid)

        # Action Buttons
        btn_action_row = QHBoxLayout()
        btn_restart = QPushButton("Restart Layanan Server")
        btn_restart.setProperty("class", "btn-secondary")
        btn_restart.clicked.connect(self.restart_service)

        btn_fix_uinput = QPushButton("Periksa Izin uinput")
        btn_fix_uinput.setProperty("class", "btn-secondary")
        btn_fix_uinput.clicked.connect(self.check_uinput_details)

        self.btn_toggle_term = QPushButton("Alihkan Smart Terminal")
        self.btn_toggle_term.setProperty("class", "btn-secondary")
        self.btn_toggle_term.clicked.connect(self.toggle_smart_terminal)

        btn_action_row.addWidget(btn_restart)
        btn_action_row.addWidget(btn_fix_uinput)
        btn_action_row.addWidget(self.btn_toggle_term)
        btn_action_row.addStretch()
        diag_layout.addLayout(btn_action_row)

        layout.addWidget(card_diag)

        # Live Log Terminal
        card_log = QFrame()
        card_log.setProperty("class", "card-panel")
        log_layout = QVBoxLayout(card_log)
        log_layout.setContentsMargins(16, 14, 16, 14)
        log_layout.setSpacing(8)

        log_head = QHBoxLayout()
        log_title = QLabel("LOG AKTIVITAS SERVER HOST")
        log_title.setProperty("class", "card-header-title")
        log_head.addWidget(log_title)
        log_head.addStretch()

        btn_refresh_log = QPushButton("Muat Ulang Log")
        btn_refresh_log.setProperty("class", "btn-secondary")
        btn_refresh_log.clicked.connect(self.update_log_viewer)
        log_head.addWidget(btn_refresh_log)
        log_layout.addLayout(log_head)

        self.log_viewer = QTextEdit()
        self.log_viewer.setObjectName("logViewer")
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMinimumHeight(140)
        log_layout.addWidget(self.log_viewer)

        layout.addWidget(card_log, 1)

        return page

    # ── Logika Status & Pembaruan Data ──
    def refresh_status(self):
        # 1. Update PIN Keycaps
        pin = None
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/api/pairing/pin", headers={"User-Agent": "DigiGUI"})
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                if resp.status == 200:
                    d = json.loads(resp.read().decode('utf-8'))
                    pin = d.get("pin")
        except Exception:
            pass

        if not pin:
            pin = pairing_manager.get_or_create_pin()

        pin_str = str(pin).strip()
        for i in range(6):
            char = pin_str[i] if i < len(pin_str) else "-"
            self.pin_keycaps[i].setText(char)

        # 2. Update QR Code & Wi-Fi URL
        target_ip = get_preferred_ip()
        url = f"http://{target_ip}:8080"
        self.lbl_wifi_url.setText(url)
        self.generate_qr(url)

        # 3. Server Check
        online = self.check_server_online()
        if online:
            self.lbl_server_status.setText("SERVER AKTIF (PORT 8080)")
            self.lbl_server_status.setStyleSheet(
                "background-color: #238636; color: #ffffff; font-weight: 700; "
                "padding: 5px 12px; border-radius: 12px; font-size: 11px;"
            )
            self.lbl_svc_status.setText("AKTIF (Running)")
            self.lbl_svc_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #3fb950;")
            self.lbl_footer_info.setText(f"Alamat: {url} | Status: Aktif")
        else:
            self.lbl_server_status.setText("SERVER TERHENTI")
            self.lbl_server_status.setStyleSheet(
                "background-color: #da3633; color: #ffffff; font-weight: 700; "
                "padding: 5px 12px; border-radius: 12px; font-size: 11px;"
            )
            self.lbl_svc_status.setText("TERHENTI (Stopped)")
            self.lbl_svc_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #da3633;")
            self.lbl_footer_info.setText("Server tidak aktif. Klik 'Restart Layanan Server'.")

        # 4. uinput permission check
        uinput_ok = os.access('/dev/uinput', os.W_OK)
        if uinput_ok:
            self.lbl_uinput_status.setText("TERSEDIA (Izin W/R Siap)")
            self.lbl_uinput_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #3fb950;")
        else:
            self.lbl_uinput_status.setText("TERBATAS (Perlu Udev Rule)")
            self.lbl_uinput_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #e3b341;")

        # 4b. Smart Terminal integration check
        if self.is_smart_terminal_enabled():
            self.lbl_smart_term_status.setText("AKTIF (Otomatis)")
            self.lbl_smart_term_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #3fb950;")
            self.btn_toggle_term.setText("Nonaktifkan Smart Terminal")
        else:
            self.lbl_smart_term_status.setText("NONAKTIF")
            self.lbl_smart_term_status.setStyleSheet("font-weight: 800; font-size: 13px; color: #8b949e;")
            self.btn_toggle_term.setText("Aktifkan Smart Terminal")

        # 5. Update Paired Devices Table
        devs = pairing_manager.get_paired_list()
        self.lbl_paired_count.setText(f"{len(devs)} Perangkat Terdaftar")
        self.table_devs.setRowCount(len(devs))
        for row, dev in enumerate(devs):
            dev_name = dev.get("name", "Unknown")
            self.table_devs.setItem(row, 0, QTableWidgetItem(dev_name))
            self.table_devs.setItem(row, 1, QTableWidgetItem(dev.get("ip", "-")))
            self.table_devs.setItem(row, 2, QTableWidgetItem(dev.get("paired_at", "-")))

            btn_del = QPushButton("Putuskan")
            btn_del.setProperty("class", "btn-danger")
            dev_id = dev.get("device_id")
            btn_del.clicked.connect(lambda ch, d=dev_id: self.unpair_device(d))
            self.table_devs.setCellWidget(row, 3, btn_del)

        # 6. Update License Display
        lic = license_manager.get_info()
        tier = lic.get("tier", "trial")
        plan_name = lic.get("plan_name", "Free Trial")
        days = lic.get("days_left", 0)

        self.lbl_lic_status_text.setText(f"{plan_name} - Status: Aktif")
        if days >= 0:
            self.lbl_lic_days.setText(f"Masa Berlaku: {days} Hari Tersisa (Hingga {lic.get('expires_at', '-')})")
        else:
            self.lbl_lic_days.setText("Masa Berlaku: Seumur Hidup (Permanen)")

        self.badge_lic_tier.setText(tier.upper())
        if tier == "lifetime":
            self.badge_lic_tier.setStyleSheet("background-color: #ff6b00; color: #ffffff; font-weight: 800; padding: 6px 16px; border-radius: 6px;")
        elif tier == "monthly":
            self.badge_lic_tier.setStyleSheet("background-color: #1f6feb; color: #ffffff; font-weight: 800; padding: 6px 16px; border-radius: 6px;")
        else:
            self.badge_lic_tier.setStyleSheet("background-color: #238636; color: #ffffff; font-weight: 800; padding: 6px 16px; border-radius: 6px;")

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
        self.lbl_qr_img.setPixmap(pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def check_server_online(self):
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/api/pairing/pin", headers={"User-Agent": "DigiGUI"})
            with urllib.request.urlopen(req, timeout=0.5) as resp:
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
        url = self.lbl_wifi_url.text()
        QApplication.clipboard().setText(url)
        QMessageBox.information(self, "Tersalin", f"URL {url} telah disalin ke papan klip.")

    def open_in_browser(self):
        url = self.lbl_wifi_url.text()
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

    def unpair_all_devices(self):
        reply = QMessageBox.question(
            self, "Konfirmasi", "Apakah Anda yakin ingin memutuskan semua perangkat yang terdaftar?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            pairing_manager.unpair_all()
            self.refresh_status()

    def activate_key_submit(self):
        key = self.txt_license_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Kunci Kosong", "Masukkan kunci lisensi terlebih dahulu.")
            return
        success, msg = license_manager.activate_key(key)
        if success:
            QMessageBox.information(self, "Aktivasi Sukses", msg)
            self.txt_license_input.clear()
            self.refresh_status()
        else:
            QMessageBox.warning(self, "Aktivasi Gagal", msg)

    def check_uinput_details(self):
        ok = os.access('/dev/uinput', os.W_OK)
        if ok:
            QMessageBox.information(self, "Izin Kernel uinput", "Izin akses /dev/uinput sudah benar dan siap digunakan.")
        else:
            msg = (
                "Akses tulis ke /dev/uinput terbatas.\n\n"
                "Jalankan skrip berikut di terminal untuk memasang rule udev:\n"
                "sudo bash setup-uinput.sh"
            )
            QMessageBox.warning(self, "Izin Kernel uinput", msg)

    def update_log_viewer(self):
        try:
            out = subprocess.check_output(
                ["journalctl", "-u", "digikeyboard", "-n", "35", "--no-pager"],
                universal_newlines=True, stderr=subprocess.DEVNULL
            )
            self.log_viewer.setPlainText(out)
            sb = self.log_viewer.verticalScrollBar()
            sb.setValue(sb.maximum())
        except Exception as e:
            self.log_viewer.setPlainText(f"Gagal membaca log: {e}")

    def is_smart_terminal_enabled(self):
        flag_file = os.path.expanduser('~/.config/digismartdeck/smart_terminal_enabled')
        return os.path.exists(flag_file)

    def toggle_smart_terminal(self):
        flag_file = os.path.expanduser('~/.config/digismartdeck/smart_terminal_enabled')
        os.makedirs(os.path.dirname(flag_file), exist_ok=True)
        if os.path.exists(flag_file):
            try:
                os.remove(flag_file)
            except Exception:
                pass
        else:
            try:
                with open(flag_file, 'w', encoding='utf-8') as f:
                    f.write('1\n')
            except Exception:
                pass
            self.ensure_bashrc_hook()
        self.refresh_all_status()

    def ensure_bashrc_hook(self):
        bashrc = os.path.expanduser('~/.bashrc')
        hook_marker = 'DIGI_TERM_SUPERVISED'
        hook_code = '\n# DigiSmartDeck Smart Terminal Integration\nif [[ $- == *i* && -t 0 && -t 1 && -z "$DIGI_TERM_SUPERVISED" && -z "$DIGI_TERM_DISABLE" && -f "$HOME/.config/digismartdeck/smart_terminal_enabled" && -x "$HOME/.local/bin/digi-term" ]]; then exec "$HOME/.local/bin/digi-term"; fi\n'
        if os.path.exists(bashrc):
            try:
                with open(bashrc, 'r', encoding='utf-8') as f:
                    content = f.read()
                if hook_marker not in content:
                    with open(bashrc, 'a', encoding='utf-8') as f:
                        f.write(hook_code)
            except Exception:
                pass
        # Pasang juga ke .zshrc jika ada
        zshrc = os.path.expanduser('~/.zshrc')
        if os.path.exists(zshrc):
            try:
                with open(zshrc, 'r', encoding='utf-8') as f:
                    content = f.read()
                if hook_marker not in content:
                    with open(zshrc, 'a', encoding='utf-8') as f:
                        f.write(hook_code)
            except Exception:
                pass


def acquire_single_instance_lock():
    """Mencegah multiple instance GUI berjalan bersamaan."""
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_socket.bind('\0digikeyboard_host_gui_lock')
        return lock_socket
    except (socket.error, OSError):
        try:
            subprocess.run(['wmctrl', '-x', '-a', 'digikeyboard_gui.py'], timeout=0.5)
        except Exception:
            pass
        return None


def main():
    lock = acquire_single_instance_lock()
    if not lock:
        print("[*] DigiSmartDeck Host Manager sudah berjalan di sistem. Mengaktifkan jendela yang ada.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("DigiSmartDeck Host")
    gui = DigiSmartDeckGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
