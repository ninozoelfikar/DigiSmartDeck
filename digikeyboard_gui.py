#!/usr/bin/env python3
"""
DigiSmartDeck Host Manager (Linux Desktop Edition)
Professional PC Companion & Hardware Daemon Control Center.
Crafted for DigiSmartDeck (SaaS & Hardware Virtualization).

Strict compliance:
- Zero emojis / zero emoticons
- Industrial clean UX (Subtle borders, high contrast, obsidian-slate theme)
- Mechanical click acoustic feedback on interactive actions
- Thread-safe background monitoring and polling
"""

import os
import sys
import io
import json
import socket
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QTabWidget, QTextEdit,
    QProgressBar, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor

import qrcode
from auth_manager import pairing_manager, license_manager

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, "assets", "icon.png")


def load_version_str():
    """Membaca string versi resmi dari file VERSION."""
    ver_file = os.path.join(APP_DIR, "VERSION")
    if os.path.exists(ver_file):
        try:
            with open(ver_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "1.21.3.1"


def get_preferred_ip():
    """Mengambil IP jaringan lokal terbaik dengan prioritas Wi-Fi / Ethernet fisik."""
    candidates = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.4)
        s.connect(('8.8.8.8', 80))
        main_ip = s.getsockname()[0]
        s.close()
        candidates.append(main_ip)
    except Exception:
        pass

    try:
        out = subprocess.check_output(['hostname', '-I'], universal_newlines=True, timeout=1).strip()
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


class StatusWorker(QThread):
    """Worker background untuk polling status server dan log tanpa memblokir thread UI."""
    data_ready = pyqtSignal(dict)

    def run(self):
        result = {}
        # 1. Fetch live PIN from local server
        pin = None
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/api/pairing/pin", headers={"User-Agent": "DigiSmartDeckDesktop"})
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    pin = data.get("pin")
        except Exception:
            pass

        if not pin:
            pin = pairing_manager.get_or_create_pin()
        result['pin'] = pin

        # 2. Server availability & latency check
        server_online = False
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/api/info", headers={"User-Agent": "DigiSmartDeckDesktop"})
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                server_online = (resp.status == 200)
        except Exception:
            server_online = False
        result['server_online'] = server_online

        # 3. /dev/uinput access
        result['uinput_ok'] = os.access('/dev/uinput', os.W_OK)

        # 4. Smart terminal status
        flag_file = os.path.expanduser('~/.config/digismartdeck/smart_terminal_enabled')
        result['smart_term_active'] = os.path.exists(flag_file)

        # 5. Paired clients & licenses
        try:
            result['devices'] = pairing_manager.get_paired_list()
        except Exception:
            result['devices'] = []

        try:
            result['license'] = license_manager.get_info()
        except Exception:
            result['license'] = {}

        self.data_ready.emit(result)


class DigiSmartDeckHostWindow(QMainWindow):
    """Antarmuka desktop profesional untuk manajemen PC Host DigiSmartDeck."""

    def __init__(self):
        super().__init__()
        self.version = load_version_str()
        self.setWindowTitle(f"DigiSmartDeck Host Manager v{self.version}")
        self.resize(1000, 720)
        self.setMinimumSize(920, 640)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.worker = StatusWorker()
        self.worker.data_ready.connect(self.on_status_updated)

        self.current_pin = "------"
        self.current_ip = get_preferred_ip()

        self.init_theme()
        self.init_ui()

        # Polling berkala (2500 ms) via background worker
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.trigger_refresh)
        self.poll_timer.start(2500)

        # Pemicuan awal
        self.trigger_refresh()

    def init_theme(self):
        """Menerapkan tema visual obsidian profesional (standar industri tooling developer)."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0e14;
            }
            QWidget#rootWidget {
                background-color: #0b0e14;
                color: #e6edf3;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Ubuntu", sans-serif;
            }
            QLabel {
                color: #e6edf3;
            }
            
            /* Header */
            QFrame#headerDeck {
                background-color: #12161f;
                border-bottom: 1px solid #1f2633;
            }
            
            /* Tabs Navigation */
            QTabWidget::pane {
                border: 1px solid #1f2633;
                background-color: #0f121a;
                border-radius: 8px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #141824;
                color: #8b949e;
                font-size: 12px;
                font-weight: 600;
                padding: 10px 24px;
                margin-right: 4px;
                border: 1px solid #1f2633;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:hover {
                background-color: #1c2230;
                color: #c9d1d9;
            }
            QTabBar::tab:selected {
                background-color: #0f121a;
                color: #58a6ff;
                border-color: #1f2633;
                border-top: 2px solid #58a6ff;
            }
            
            /* Card Containers */
            QFrame.panelCard {
                background-color: #141824;
                border: 1px solid #232a38;
                border-radius: 8px;
            }
            QFrame.panelCardInset {
                background-color: #0b0e14;
                border: 1px solid #1a202c;
                border-radius: 6px;
            }
            
            /* Typography Helpers */
            QLabel.sectionTitle {
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.8px;
                color: #58a6ff;
                text-transform: uppercase;
            }
            QLabel.bodyMuted {
                font-size: 12px;
                color: #8b949e;
                line-height: 1.4;
            }
            
            /* Keycaps */
            QLabel.keycapDigit {
                background-color: #0b0e14;
                border: 2px solid #2d3748;
                border-radius: 8px;
                font-family: "JetBrains Mono", "Fira Code", monospace;
                font-size: 26px;
                font-weight: 800;
                color: #58a6ff;
                min-width: 44px;
                max-width: 48px;
                min-height: 50px;
                max-height: 54px;
                qproperty-alignment: AlignCenter;
            }
            
            /* Buttons */
            QPushButton {
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                outline: none;
            }
            QPushButton.btnPrimary {
                background-color: #1f6feb;
                color: #ffffff;
                border: 1px solid #388bfd;
            }
            QPushButton.btnPrimary:hover {
                background-color: #388bfd;
            }
            QPushButton.btnPrimary:pressed {
                background-color: #1158c7;
            }
            
            QPushButton.btnSecondary {
                background-color: #1a2130;
                color: #c9d1d9;
                border: 1px solid #2d3748;
            }
            QPushButton.btnSecondary:hover {
                background-color: #242d40;
                color: #ffffff;
                border-color: #4a5568;
            }
            QPushButton.btnSecondary:pressed {
                background-color: #141a26;
            }
            
            QPushButton.btnDanger {
                background-color: #211215;
                color: #f85149;
                border: 1px solid #5a1e22;
            }
            QPushButton.btnDanger:hover {
                background-color: #da3633;
                color: #ffffff;
                border-color: #f85149;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #0b0e14;
                border: 1px solid #1f2633;
                border-radius: 6px;
                gridline-color: #161b22;
                color: #c9d1d9;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #141824;
                color: #8b949e;
                font-size: 11px;
                font-weight: 700;
                padding: 8px;
                border: 1px solid #1f2633;
            }
            
            /* Inputs */
            QLineEdit {
                background-color: #0b0e14;
                border: 1px solid #2d3748;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 13px;
                font-family: "JetBrains Mono", monospace;
            }
            QLineEdit:focus {
                border: 1px solid #58a6ff;
            }
            
            /* Logs */
            QTextEdit#logTerminal {
                background-color: #07090e;
                border: 1px solid #1f2633;
                border-radius: 6px;
                color: #7ee787;
                font-family: "JetBrains Mono", "Courier New", monospace;
                font-size: 11px;
                padding: 10px;
            }
            
            /* Status Badges */
            QLabel.badgeStatusOnline {
                background-color: #12281a;
                color: #3fb950;
                border: 1px solid #238636;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel.badgeStatusOffline {
                background-color: #2b1114;
                color: #f85149;
                border: 1px solid #da3633;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel.badgeInfo {
                background-color: #121d2f;
                color: #58a6ff;
                border: 1px solid #1f6feb;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }
        """)

    def init_ui(self):
        root = QWidget(self)
        root.setObjectName("rootWidget")
        self.setCentralWidget(root)

        main_vbox = QVBoxLayout(root)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # ── 1. Top Navigation / Header Bar ──
        header = QFrame()
        header.setObjectName("headerDeck")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)
        header_layout.setSpacing(14)

        if os.path.exists(ICON_PATH):
            logo_lbl = QLabel()
            pix = QPixmap(ICON_PATH).scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            header_layout.addWidget(logo_lbl)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        app_title = QLabel("DIGISMARTDECK HOST")
        app_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #ffffff; letter-spacing: 0.6px;")
        app_subtitle = QLabel("PC Daemon & Hardware Emulation Bridge")
        app_subtitle.setStyleSheet("font-size: 11px; color: #8b949e;")
        title_vbox.addWidget(app_title)
        title_vbox.addWidget(app_subtitle)
        header_layout.addLayout(title_vbox)

        header_layout.addStretch()

        # Status Indicators
        self.badge_server = QLabel("PORT 8080 : RUNNING")
        self.badge_server.setProperty("class", "badgeStatusOnline")
        header_layout.addWidget(self.badge_server)

        self.badge_uinput = QLabel("UINPUT : HARDWARE READY")
        self.badge_uinput.setProperty("class", "badgeInfo")
        header_layout.addWidget(self.badge_uinput)

        btn_open_browser = QPushButton("Buka Antarmuka Web")
        btn_open_browser.setProperty("class", "btnPrimary")
        btn_open_browser.clicked.connect(self.action_open_browser)
        header_layout.addWidget(btn_open_browser)

        main_vbox.addWidget(header)

        # ── 2. Content Tabs ──
        content_container = QWidget()
        content_vbox = QVBoxLayout(content_container)
        content_vbox.setContentsMargins(20, 16, 20, 16)
        content_vbox.setSpacing(12)

        self.tabs = QTabWidget()
        self.tab_pairing = self.create_tab_pairing()
        self.tab_devices = self.create_tab_devices()
        self.tab_license = self.create_tab_license()
        self.tab_system = self.create_tab_system()

        self.tabs.addTab(self.tab_pairing, "Pusat Kendali & Pairing")
        self.tabs.addTab(self.tab_devices, "Perangkat Terhubung")
        self.tabs.addTab(self.tab_license, "Lisensi SaaS")
        self.tabs.addTab(self.tab_system, "Status Sistem & Log")

        content_vbox.addWidget(self.tabs)
        main_vbox.addWidget(content_container, 1)

        # ── 3. Footer Bar ──
        footer = QFrame()
        footer.setStyleSheet("background-color: #12161f; border-top: 1px solid #1f2633; padding: 6px 20px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 6, 20, 6)

        self.lbl_footer_status = QLabel(f"Host IP: {self.current_ip} | Endpoint: http://{self.current_ip}:8080")
        self.lbl_footer_status.setStyleSheet("color: #8b949e; font-size: 11px;")
        footer_layout.addWidget(self.lbl_footer_status)

        footer_layout.addStretch()

        ver_label = QLabel(f"DigiSmartDeck v{self.version} - Zero Telemetry Architecture")
        ver_label.setStyleSheet("color: #484f58; font-size: 11px; font-family: monospace;")
        footer_layout.addWidget(ver_label)

        main_vbox.addWidget(footer)

    # ── Tab 1: Pusat Kendali & Pairing ──
    def create_tab_pairing(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        top_cards = QHBoxLayout()
        top_cards.setSpacing(16)

        # Card A: PIN Display
        card_pin = QFrame()
        card_pin.setProperty("class", "panelCard")
        pin_vbox = QVBoxLayout(card_pin)
        pin_vbox.setContentsMargins(18, 16, 18, 16)
        pin_vbox.setSpacing(10)

        t_pin = QLabel("PIN OTORISASI PERANGKAT")
        t_pin.setProperty("class", "sectionTitle")
        pin_vbox.addWidget(t_pin)

        d_pin = QLabel("Masukkan 6 digit kode keamanan di bawah pada aplikasi ponsel Anda:")
        d_pin.setProperty("class", "bodyMuted")
        pin_vbox.addWidget(d_pin)

        self.pin_boxes = []
        box_row = QHBoxLayout()
        box_row.setSpacing(8)
        box_row.setAlignment(Qt.AlignCenter)
        for _ in range(6):
            box = QLabel("-")
            box.setProperty("class", "keycapDigit")
            box_row.addWidget(box)
            self.pin_boxes.append(box)
        pin_vbox.addLayout(box_row)

        sub_info = QLabel("Perangkat otomatis terhubung begitu 6 digit selesai diketik.")
        sub_info.setStyleSheet("color: #3fb950; font-size: 11px; font-weight: 600;")
        sub_info.setAlignment(Qt.AlignCenter)
        pin_vbox.addWidget(sub_info)

        btn_row = QHBoxLayout()
        btn_copy = QPushButton("Salin PIN")
        btn_copy.setProperty("class", "btnSecondary")
        btn_copy.clicked.connect(self.action_copy_pin)

        btn_regen = QPushButton("Acak Ulang PIN")
        btn_regen.setProperty("class", "btnSecondary")
        btn_regen.clicked.connect(self.action_regen_pin)

        btn_row.addWidget(btn_copy)
        btn_row.addWidget(btn_regen)
        pin_vbox.addLayout(btn_row)

        top_cards.addWidget(card_pin, 1)

        # Card B: QR Code & Connection Address
        card_qr = QFrame()
        card_qr.setProperty("class", "panelCard")
        qr_layout = QHBoxLayout(card_qr)
        qr_layout.setContentsMargins(18, 16, 18, 16)
        qr_layout.setSpacing(16)

        self.lbl_qr = QLabel()
        self.lbl_qr.setFixedSize(124, 124)
        self.lbl_qr.setStyleSheet("background-color: #ffffff; border-radius: 6px; padding: 2px;")
        self.lbl_qr.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(self.lbl_qr)

        qr_text_vbox = QVBoxLayout()
        qr_text_vbox.setSpacing(6)

        t_conn = QLabel("AKSES CEPAT VIA JARINGAN")
        t_conn.setProperty("class", "sectionTitle")
        qr_text_vbox.addWidget(t_conn)

        d_conn = QLabel("Pindai QR code menggunakan kamera ponsel atau buka URL berikut:")
        d_conn.setProperty("class", "bodyMuted")
        qr_text_vbox.addWidget(d_conn)

        self.lbl_url = QLabel(f"http://{self.current_ip}:8080")
        self.lbl_url.setStyleSheet("font-family: monospace; font-size: 13px; font-weight: 700; color: #58a6ff;")
        self.lbl_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        qr_text_vbox.addWidget(self.lbl_url)

        btn_copy_url = QPushButton("Salin Tautan URL")
        btn_copy_url.setProperty("class", "btnSecondary")
        btn_copy_url.clicked.connect(self.action_copy_url)
        qr_text_vbox.addWidget(btn_copy_url)

        qr_layout.addLayout(qr_text_vbox)
        top_cards.addWidget(card_qr, 1)

        layout.addLayout(top_cards)

        # Bottom Architecture Guide
        card_guide = QFrame()
        card_guide.setProperty("class", "panelCard")
        guide_vbox = QVBoxLayout(card_guide)
        guide_vbox.setContentsMargins(18, 16, 18, 16)
        guide_vbox.setSpacing(10)

        t_guide = QLabel("PANDUAN KONEKSI HARDWARE EMULATION")
        t_guide.setProperty("class", "sectionTitle")
        guide_vbox.addWidget(t_guide)

        cols_hbox = QHBoxLayout()
        cols_hbox.setSpacing(20)

        c1 = QVBoxLayout()
        c1.addWidget(QLabel("1. Koneksi Nirkabel Wi-Fi LAN"))
        c1.itemAt(0).widget().setStyleSheet("font-size: 12px; font-weight: 700; color: #e6edf3;")
        desc1 = QLabel("Pastikan ponsel berada di subnet Wi-Fi yang sama dengan PC host. Latensi transmisi umumnya berkisar antara 8-15 milidetik.")
        desc1.setProperty("class", "bodyMuted")
        desc1.setWordWrap(True)
        c1.addWidget(desc1)
        cols_hbox.addLayout(c1)

        c2 = QVBoxLayout()
        c2.addWidget(QLabel("2. Koneksi Kabel USB (<1ms)"))
        c2.itemAt(0).widget().setStyleSheet("font-size: 12px; font-weight: 700; color: #e6edf3;")
        desc2 = QLabel("Sambungkan kabel data USB, aktifkan USB Debugging (ADB) atau USB Tethering. Bebas interferensi frekuensi dengan latensi sub-milidetik.")
        desc2.setProperty("class", "bodyMuted")
        desc2.setWordWrap(True)
        c2.addWidget(desc2)
        cols_hbox.addLayout(c2)

        guide_vbox.addLayout(cols_hbox)
        layout.addWidget(card_guide)
        layout.addStretch()

        return page

    # ── Tab 2: Perangkat Terhubung ──
    def create_tab_devices(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        card = QFrame()
        card.setProperty("class", "panelCard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(18, 16, 18, 16)
        vbox.setSpacing(12)

        h_top = QHBoxLayout()
        t = QLabel("DAFTAR PERANGKAT TEROTORISASI (PAIRED CLIENTS)")
        t.setProperty("class", "sectionTitle")
        h_top.addWidget(t)
        h_top.addStretch()

        self.lbl_dev_count = QLabel("0 Perangkat Terdaftar")
        self.lbl_dev_count.setStyleSheet("color: #8b949e; font-size: 12px;")
        h_top.addWidget(self.lbl_dev_count)

        btn_unpair_all = QPushButton("Putuskan Semua")
        btn_unpair_all.setProperty("class", "btnDanger")
        btn_unpair_all.clicked.connect(self.action_unpair_all)
        h_top.addWidget(btn_unpair_all)
        vbox.addLayout(h_top)

        desc = QLabel("Perangkat berikut memiliki otorisasi penuh untuk mengendalikan input mouse, keyboard, dan eksekusi prompt di PC.")
        desc.setProperty("class", "bodyMuted")
        vbox.addWidget(desc)

        self.table_devs = QTableWidget(0, 4)
        self.table_devs.setHorizontalHeaderLabels(["Nama / Label Klien", "Alamat IP", "Terdaftar Pada", "Aksi"])
        self.table_devs.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_devs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_devs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_devs.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_devs.setSelectionMode(QTableWidget.NoSelection)
        self.table_devs.setMinimumHeight(260)
        vbox.addWidget(self.table_devs)

        layout.addWidget(card)
        return page

    # ── Tab 3: Lisensi SaaS ──
    def create_tab_license(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        card_status = QFrame()
        card_status.setProperty("class", "panelCard")
        st_layout = QHBoxLayout(card_status)
        st_layout.setContentsMargins(18, 16, 18, 16)

        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(4)
        t_lic = QLabel("STATUS LISENSI SAAS HOST")
        t_lic.setProperty("class", "sectionTitle")
        self.lbl_lic_plan = QLabel("Memuat informasi lisensi...")
        self.lbl_lic_plan.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        self.lbl_lic_expiry = QLabel("Masa Berlaku: -")
        self.lbl_lic_expiry.setStyleSheet("font-size: 12px; color: #8b949e;")

        info_vbox.addWidget(t_lic)
        info_vbox.addWidget(self.lbl_lic_plan)
        info_vbox.addWidget(self.lbl_lic_expiry)
        st_layout.addLayout(info_vbox)
        st_layout.addStretch()

        self.badge_tier = QLabel("TRIAL")
        self.badge_tier.setStyleSheet("background-color: #1f6feb; color: #ffffff; font-weight: 800; padding: 6px 18px; border-radius: 6px; font-size: 12px;")
        st_layout.addWidget(self.badge_tier)
        layout.addWidget(card_status)

        # Activation Form
        card_act = QFrame()
        card_act.setProperty("class", "panelCard")
        act_vbox = QVBoxLayout(card_act)
        act_vbox.setContentsMargins(18, 16, 18, 16)
        act_vbox.setSpacing(10)

        t_act = QLabel("AKTIVASI KUNCI LISENSI 20-DIGIT")
        t_act.setProperty("class", "sectionTitle")
        act_vbox.addWidget(t_act)

        act_desc = QLabel("Format kunci lisensi resmi: DLIFE-XXXXX-XXXXX-XXXXX atau DMONT-XXXXX-XXXXX-XXXXX")
        act_desc.setProperty("class", "bodyMuted")
        act_vbox.addWidget(act_desc)

        act_hbox = QHBoxLayout()
        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX")
        act_hbox.addWidget(self.txt_key, 1)

        btn_activate = QPushButton("Aktifkan Lisensi")
        btn_activate.setProperty("class", "btnPrimary")
        btn_activate.clicked.connect(self.action_activate_license)
        act_hbox.addWidget(btn_activate)

        act_vbox.addLayout(act_hbox)
        layout.addWidget(card_act)
        layout.addStretch()

        return page

    # ── Tab 4: Status Sistem & Log ──
    def create_tab_system(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        card_diag = QFrame()
        card_diag.setProperty("class", "panelCard")
        diag_vbox = QVBoxLayout(card_diag)
        diag_vbox.setContentsMargins(18, 16, 18, 16)
        diag_vbox.setSpacing(12)

        t_diag = QLabel("KESIAPAN SUBSISTEM LINUX HOST")
        t_diag.setProperty("class", "sectionTitle")
        diag_vbox.addWidget(t_diag)

        diag_grid = QHBoxLayout()
        diag_grid.setSpacing(12)

        # Sub-panel 1: uinput
        p1 = QFrame()
        p1.setProperty("class", "panelCardInset")
        v1 = QVBoxLayout(p1)
        v1.addWidget(QLabel("Kernel Driver (/dev/uinput)"))
        v1.itemAt(0).widget().setStyleSheet("font-size: 11px; color: #8b949e;")
        self.lbl_diag_uinput = QLabel("MEMERIKSA...")
        self.lbl_diag_uinput.setStyleSheet("font-size: 13px; font-weight: 700; color: #3fb950;")
        v1.addWidget(self.lbl_diag_uinput)
        diag_grid.addWidget(p1)

        # Sub-panel 2: systemd service
        p2 = QFrame()
        p2.setProperty("class", "panelCardInset")
        v2 = QVBoxLayout(p2)
        v2.addWidget(QLabel("Layanan Latar (digikeyboard.service)"))
        v2.itemAt(0).widget().setStyleSheet("font-size: 11px; color: #8b949e;")
        self.lbl_diag_service = QLabel("MEMERIKSA...")
        self.lbl_diag_service.setStyleSheet("font-size: 13px; font-weight: 700; color: #3fb950;")
        v2.addWidget(self.lbl_diag_service)
        diag_grid.addWidget(p2)

        # Sub-panel 3: smart terminal
        p3 = QFrame()
        p3.setProperty("class", "panelCardInset")
        v3 = QVBoxLayout(p3)
        v3.addWidget(QLabel("Integrasi Smart Terminal CLI"))
        v3.itemAt(0).widget().setStyleSheet("font-size: 11px; color: #8b949e;")
        self.lbl_diag_term = QLabel("MEMERIKSA...")
        self.lbl_diag_term.setStyleSheet("font-size: 13px; font-weight: 700; color: #3fb950;")
        v3.addWidget(self.lbl_diag_term)
        diag_grid.addWidget(p3)

        diag_vbox.addLayout(diag_grid)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_restart = QPushButton("Restart Layanan Server")
        btn_restart.setProperty("class", "btnSecondary")
        btn_restart.clicked.connect(self.action_restart_service)

        self.btn_toggle_term = QPushButton("Alihkan Smart Terminal")
        self.btn_toggle_term.setProperty("class", "btnSecondary")
        self.btn_toggle_term.clicked.connect(self.action_toggle_smart_terminal)

        btn_row.addWidget(btn_restart)
        btn_row.addWidget(self.btn_toggle_term)
        btn_row.addStretch()
        diag_vbox.addLayout(btn_row)

        layout.addWidget(card_diag)

        # Live Log Terminal
        card_log = QFrame()
        card_log.setProperty("class", "panelCard")
        log_vbox = QVBoxLayout(card_log)
        log_vbox.setContentsMargins(18, 16, 18, 16)
        log_vbox.setSpacing(10)

        log_head = QHBoxLayout()
        t_log = QLabel("LOG AKTIVITAS SERVER HOST (JOURNALCTL)")
        t_log.setProperty("class", "sectionTitle")
        log_head.addWidget(t_log)
        log_head.addStretch()

        btn_refresh_log = QPushButton("Muat Ulang Log")
        btn_refresh_log.setProperty("class", "btnSecondary")
        btn_refresh_log.clicked.connect(self.action_refresh_logs)
        log_head.addWidget(btn_refresh_log)
        log_vbox.addLayout(log_head)

        self.log_terminal = QTextEdit()
        self.log_terminal.setObjectName("logTerminal")
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setMinimumHeight(180)
        log_vbox.addWidget(self.log_terminal)

        layout.addWidget(card_log, 1)

        return page

    # ── Data Polling & UI Sync ──
    def trigger_refresh(self):
        if not self.worker.isRunning():
            self.worker.start()

    def on_status_updated(self, data):
        # 1. PIN Keycaps
        pin_str = str(data.get('pin', '------')).strip()
        self.current_pin = pin_str
        for i in range(6):
            ch = pin_str[i] if i < len(pin_str) else "-"
            self.pin_boxes[i].setText(ch)

        # 2. Server Status
        online = data.get('server_online', False)
        if online:
            self.badge_server.setText("PORT 8080 : RUNNING")
            self.badge_server.setProperty("class", "badgeStatusOnline")
            self.lbl_diag_service.setText("AKTIF (Running)")
            self.lbl_diag_service.setStyleSheet("font-size: 13px; font-weight: 700; color: #3fb950;")
        else:
            self.badge_server.setText("PORT 8080 : STOPPED")
            self.badge_server.setProperty("class", "badgeStatusOffline")
            self.lbl_diag_service.setText("TERHENTI (Stopped)")
            self.lbl_diag_service.setStyleSheet("font-size: 13px; font-weight: 700; color: #f85149;")
        self.badge_server.style().polish(self.badge_server)

        # 3. uinput
        uinput_ok = data.get('uinput_ok', False)
        if uinput_ok:
            self.badge_uinput.setText("UINPUT : HARDWARE READY")
            self.badge_uinput.setProperty("class", "badgeInfo")
            self.lbl_diag_uinput.setText("TERSEDIA (Izin W/R Siap)")
            self.lbl_diag_uinput.setStyleSheet("font-size: 13px; font-weight: 700; color: #3fb950;")
        else:
            self.badge_uinput.setText("UINPUT : PERMISSION RESTRICTED")
            self.badge_uinput.setProperty("class", "badgeStatusOffline")
            self.lbl_diag_uinput.setText("TERBATAS (Perlu Udev Rule)")
            self.lbl_diag_uinput.setStyleSheet("font-size: 13px; font-weight: 700; color: #e3b341;")
        self.badge_uinput.style().polish(self.badge_uinput)

        # 4. Smart Terminal
        st_active = data.get('smart_term_active', False)
        if st_active:
            self.lbl_diag_term.setText("AKTIF (Otomatis)")
            self.lbl_diag_term.setStyleSheet("font-size: 13px; font-weight: 700; color: #3fb950;")
            self.btn_toggle_term.setText("Nonaktifkan Smart Terminal")
        else:
            self.lbl_diag_term.setText("NONAKTIF")
            self.lbl_diag_term.setStyleSheet("font-size: 13px; font-weight: 700; color: #8b949e;")
            self.btn_toggle_term.setText("Aktifkan Smart Terminal")

        # 5. Paired Devices
        devices = data.get('devices', [])
        self.lbl_dev_count.setText(f"{len(devices)} Perangkat Terdaftar")
        self.table_devs.setRowCount(len(devices))
        for row, dev in enumerate(devices):
            self.table_devs.setItem(row, 0, QTableWidgetItem(dev.get("name", "Unknown")))
            self.table_devs.setItem(row, 1, QTableWidgetItem(dev.get("ip", "-")))
            self.table_devs.setItem(row, 2, QTableWidgetItem(dev.get("paired_at", "-")))

            btn_unpair = QPushButton("Putuskan")
            btn_unpair.setProperty("class", "btnDanger")
            dev_id = dev.get("device_id")
            btn_unpair.clicked.connect(lambda ch, d=dev_id: self.action_unpair_device(d))
            self.table_devs.setCellWidget(row, 3, btn_unpair)

        # 6. License Info
        lic = data.get('license', {})
        tier = lic.get("tier", "trial")
        plan_name = lic.get("plan_name", "Free Trial")
        days = lic.get("days_left", 0)

        self.lbl_lic_plan.setText(f"{plan_name} - Status: Aktif")
        if days >= 0:
            self.lbl_lic_expiry.setText(f"Masa Berlaku: {days} Hari Tersisa (Hingga {lic.get('expires_at', '-')})")
        else:
            self.lbl_lic_expiry.setText("Masa Berlaku: Seumur Hidup (Permanen)")

        self.badge_tier.setText(tier.upper())
        if tier == "lifetime":
            self.badge_tier.setStyleSheet("background-color: #ff6b00; color: #ffffff; font-weight: 800; padding: 6px 18px; border-radius: 6px; font-size: 12px;")
        elif tier == "monthly":
            self.badge_tier.setStyleSheet("background-color: #1f6feb; color: #ffffff; font-weight: 800; padding: 6px 18px; border-radius: 6px; font-size: 12px;")
        else:
            self.badge_tier.setStyleSheet("background-color: #238636; color: #ffffff; font-weight: 800; padding: 6px 18px; border-radius: 6px; font-size: 12px;")

        # 7. QR Code Regeneration if IP changed
        target_ip = get_preferred_ip()
        if target_ip != self.current_ip or not self.lbl_qr.pixmap():
            self.current_ip = target_ip
            url = f"http://{target_ip}:8080"
            self.lbl_url.setText(url)
            self.lbl_footer_status.setText(f"Host IP: {target_ip} | Endpoint: {url}")
            self.render_qr(url)

    def render_qr(self, data):
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
        self.lbl_qr.setPixmap(pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # ── User Action Handlers ──
    def action_copy_pin(self):
        QApplication.clipboard().setText(self.current_pin)
        QMessageBox.information(self, "Tersalin", f"Kode PIN {self.current_pin} telah disalin ke papan klip.")

    def action_regen_pin(self):
        new_pin = pairing_manager.generate_pin()
        self.trigger_refresh()
        QMessageBox.information(self, "PIN Diperbarui", f"Kode PIN baru: {new_pin}")

    def action_copy_url(self):
        url = self.lbl_url.text()
        QApplication.clipboard().setText(url)
        QMessageBox.information(self, "Tersalin", f"Tautan {url} telah disalin ke papan klip.")

    def action_open_browser(self):
        url = self.lbl_url.text()
        subprocess.Popen(["xdg-open", url])

    def action_restart_service(self):
        srv_file = os.path.join(APP_DIR, "server.py")
        subprocess.run(["pkill", "-f", srv_file])
        subprocess.run(["pkill", "-f", "server.py"])
        QTimer.singleShot(1500, self.trigger_refresh)
        QMessageBox.information(self, "Restart Layanan", "Sinyal restart server telah dikirim ke systemd daemon.")

    def action_unpair_device(self, dev_id):
        if not dev_id:
            return
        pairing_manager.unpair_device(dev_id)
        self.trigger_refresh()

    def action_unpair_all(self):
        res = QMessageBox.question(
            self, "Konfirmasi Tindakan", "Apakah Anda yakin ingin memutuskan semua koneksi perangkat terdaftar?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            pairing_manager.unpair_all()
            self.trigger_refresh()

    def action_activate_license(self):
        key = self.txt_key.text().strip()
        if not key:
            QMessageBox.warning(self, "Kunci Kosong", "Masukkan format kunci lisensi yang valid.")
            return
        ok, msg = license_manager.activate_key(key)
        if ok:
            QMessageBox.information(self, "Aktivasi Sukses", msg)
            self.txt_key.clear()
            self.trigger_refresh()
        else:
            QMessageBox.warning(self, "Aktivasi Ditolak", msg)

    def action_toggle_smart_terminal(self):
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
            self.ensure_shell_hooks()
        self.trigger_refresh()

    def ensure_shell_hooks(self):
        hook_marker = 'DIGI_TERM_SUPERVISED'
        hook_code = '\n# DigiSmartDeck Smart Terminal Integration\nif [[ $- == *i* && -t 0 && -t 1 && -z "$DIGI_TERM_SUPERVISED" && -z "$DIGI_TERM_DISABLE" && -f "$HOME/.config/digismartdeck/smart_terminal_enabled" && -x "$HOME/.local/bin/digi-term" ]]; then exec "$HOME/.local/bin/digi-term"; fi\n'
        for rc in [os.path.expanduser('~/.bashrc'), os.path.expanduser('~/.zshrc')]:
            if os.path.exists(rc):
                try:
                    with open(rc, 'r', encoding='utf-8') as f:
                        c = f.read()
                    if hook_marker not in c:
                        with open(rc, 'a', encoding='utf-8') as f:
                            f.write(hook_code)
                except Exception:
                    pass

    def action_refresh_logs(self):
        try:
            out = subprocess.check_output(
                ["journalctl", "-u", "digikeyboard", "-n", "45", "--no-pager"],
                universal_newlines=True, stderr=subprocess.DEVNULL, timeout=2
            )
            self.log_terminal.setPlainText(out)
            sb = self.log_terminal.verticalScrollBar()
            sb.setValue(sb.maximum())
        except Exception as e:
            self.log_terminal.setPlainText(f"Gagal mengambil log: {e}")


def acquire_single_instance_lock():
    """Mencegah multiple process GUI berjalan serentak."""
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
        print("[*] DigiSmartDeck Host Manager sudah berjalan di sistem.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("DigiSmartDeck Host")
    gui = DigiSmartDeckHostWindow()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
