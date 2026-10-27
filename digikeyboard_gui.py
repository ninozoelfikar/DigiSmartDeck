#!/usr/bin/env python3
"""
DigiSmartDeck Desktop Host Manager (Modern Chromium / WebEngine Edition)
Sleek Developer Studio UI/UX adhering to the VoiceStudio aesthetic.
Zero legacy Qt widgets, frameless studio window with custom minimal controls.
"""

import os
import sys
import socket
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSizeGrip
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import Qt, QUrl, QPoint
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, "assets", "icon.png")


class StudioTitleBar(QWidget):
    """
    Titlebar studio kustom di mana logo & nama aplikasi sejajar dengan tombol kontrol jendela.
    Sesuai standar VoiceStudio:
    - Kiri: Logo icon + DigiSmartDeck
    - Tengah: Area drag window (fleksibel & bersih)
    - Kanan: Tombol kontrol jendela (minimize, maximize, close)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(42)
        self.drag_position = QPoint()

        # Layout horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 14, 0)
        layout.setSpacing(6)

        # 1. Brand Logo di kiri (sejajar dengan tombol kontrol di kanan)
        self.logo_label = QLabel(self)
        if os.path.exists(ICON_PATH):
            pix = QPixmap(ICON_PATH).scaled(
                18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(pix)
        self.logo_label.setFixedSize(18, 18)
        layout.addWidget(self.logo_label)

        # 2. Nama Aplikasi di samping logo
        self.title_label = QLabel("DigiSmartDeck", self)
        self.title_label.setStyleSheet(
            "color: #f4f4f5; font-size: 13px; font-weight: 600; font-family: 'Inter', -apple-system, sans-serif;"
        )
        layout.addWidget(self.title_label)

        # 3. Spacer fleksibel di tengah (area drag murni)
        layout.addStretch(1)

        # 4. Tombol Kontrol Jendela (Rounded Studio Standard - selaras dengan tema desain)
        self.btn_min = QPushButton("―", self)
        self.btn_min.setToolTip("Minimize")
        self.btn_min.setFixedSize(28, 28)
        self.btn_min.clicked.connect(self.parent.showMinimized)

        self.btn_max = QPushButton("□", self)
        self.btn_max.setToolTip("Maximize / Restore")
        self.btn_max.setFixedSize(28, 28)
        self.btn_max.clicked.connect(self.toggle_maximize)

        self.btn_close = QPushButton("✕", self)
        self.btn_close.setObjectName("close_btn")
        self.btn_close.setToolTip("Close")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.clicked.connect(self.parent.close)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

        self.setStyleSheet("""
            StudioTitleBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0b1226,
                    stop:0.25 #080d1c,
                    stop:0.7 #070a16,
                    stop:1 #0a1124);
                border-bottom: 1px solid rgba(59, 130, 246, 0.18);
            }
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 7px;
                color: #94a3b8;
                font-family: 'Inter', -apple-system, sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(59, 130, 246, 0.18);
                color: #ffffff;
            }
            QPushButton#close_btn:hover {
                background-color: #dc2626;
                color: #ffffff;
            }
            QToolTip {
                background-color: #0d1527;
                color: #93c5fd;
                border: 1px solid rgba(59, 130, 246, 0.45);
                border-radius: 6px;
                padding: 4px 8px;
                font-family: 'Inter', -apple-system, sans-serif;
                font-size: 11px;
                font-weight: 500;
            }
        """)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setText("□")
        else:
            self.parent.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.parent.isMaximized():
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
            event.accept()


class DigiSmartDeckHostWindow(QMainWindow):
    """Jendela desktop studio modern berbasis Chromium WebEngine dengan frameless window."""

    def __init__(self):
        super().__init__()
        # Frameless window: hilangkan OS title bar yang kaku & bertuliskan teks panjang
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.setWindowTitle("")
        self.resize(1120, 760)
        self.setMinimumSize(960, 640)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        # Root container
        container = QWidget(self)
        container.setStyleSheet("background-color: #070a14;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar kustom studio (VoiceStudio style, tanpa teks judul)
        self.title_bar = StudioTitleBar(self)
        layout.addWidget(self.title_bar)

        # WebEngine View
        self.view = QWebEngineView(self)
        settings = self.view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.view.setStyleSheet("background-color: #070a14;")

        # Arahkan ke endpoint desktop host lokal
        endpoint_url = "http://127.0.0.1:8080/desktop"
        self.view.setUrl(QUrl(endpoint_url))
        layout.addWidget(self.view)

        self.setCentralWidget(container)


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

    # Inisialisasi aplikasi Qt tanpa nama aplikasi yang bocor ke OS bar
    app = QApplication(sys.argv)
    app.setApplicationName("")
    app.setStyleSheet("""
        QToolTip {
            background-color: #0d1527;
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.45);
            border-radius: 6px;
            padding: 5px 9px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 11px;
            font-weight: 500;
        }
    """)
    gui = DigiSmartDeckHostWindow()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
