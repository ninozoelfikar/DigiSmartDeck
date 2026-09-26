# ⌨️ DigiKeyboard (Remote PC Keyboard)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-informational)](#)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](#)
[![Tech](https://img.shields.io/badge/Stack-WebSocket%20%7C%20aiohttp%20%7C%20pynput-orange.svg)](#)

> **Ubah layar HP / Tablet Anda menjadi keyboard fisik standar PC nirkabel via Wi-Fi lokal, tanpa memicu keyboard virtual HP bawaan.**  
> *Transform your smartphone or tablet into a full-fidelity wireless PC physical keyboard over local Wi-Fi, without triggering native mobile on-screen keyboards.*

---

*Read in: [Bahasa Indonesia](#-bahasa-indonesia) | [English](#-english)*

---

## 🇮🇩 Bahasa Indonesia

### 🌟 Mengapa DigiKeyboard?
Mayoritas aplikasi remote keyboard menampilkan kotak teks yang memunculkan keyboard bawaan HP (Gboard / SwiftKey). Hal ini menyulitkan akses ke tombol-tombol fungsional PC seperti **Esc, Tab, Ctrl, Alt, Win/Super, F1-F12, Backspace, Panah**, hingga **Numpad**.

**DigiKeyboard** menyajikan antarmuka visual layout keyboard fisik PC sesungguhnya langsung di layar browser HP/Tablet Anda dengan latensi ultra-rendah (1-5 ms) melalui WebSocket.

---

### ✨ Fitur Utama
1. **Layout Keyboard Fisik Lengkap di Layar:**
   - **Baris 1:** Baris Angka (`1` - `0`, `-`, `=`) dan simbol Shift lengkap + tombol Backspace lebar.
   - **Baris 2:** Tab ⇥, QWERTY, kurung siku `[ {`, `] }`, dan `\ |`.
   - **Baris 3:** Caps Lock ⇪, ASDFGHJKL, tanda baca, dan Enter ↵.
   - **Baris 4:** Shift ⇧ (Kiri & Kanan), ZXCVBNM, tanda baca, dan panah ▲.
   - **Baris 5:** Ctrl, Win/Super ⊞, Alt, Space Bar panjang, serta panah ◀ ▼ ▶.
2. **Panel Ekstensi (Bisa di-toggle):**
   - **Fn Bar:** Tombol `Esc`, `F1` s/d `F12`.
   - **Nav Bar:** `Insert`, `Delete`, `Home`, `End`, `Page Up`, `Page Down`, `Print Screen`.
   - **PC Numpad:** Blok 17 tombol kalkulator angka lengkap.
   - **Shortcut Cepat:** Tombol 1-tap untuk `Ctrl+C`, `Ctrl+V`, `Ctrl+Z`, `Ctrl+A`, `Alt+Tab`, `Win+D`.
3. **Mekanisme Khusus Layar Sentuh:**
   - **Latch / Sticky Modifier:** Ketuk `Ctrl`, `Alt`, atau `Shift` satu kali untuk mengunci status, tekan karakter berikutnya, lalu modifier otomatis terlepas.
   - **Multi-Touch:** Mendukung penekanan tombol kombinasi dengan multi-jari simultan.
   - **Haptic Feedback:** Getaran lembut saat tombol virtual ditekan (bisa diaktifkan/dinonaktifkan).
4. **Smart LAN Detection & QR Code:**
   - Secara otomatis mendeteksi alamat IP Wi-Fi lokal fisik Anda (mengabaikan interface VPN/Docker seperti Cloudflare WARP), dan menampilkan QR code di terminal PC untuk koneksi instan.

---

### 🚀 Cara Menjalankan

#### Persyaratan
- PC dan HP/Tablet terhubung ke **jaringan Wi-Fi yang sama**.
- Python 3.8 atau lebih baru.

#### Di Linux PC:
Cara termudah menggunakan installer otomatis:
```bash
cd digikeyboard
chmod +x install-linux.sh
./install-linux.sh
```

Atau jalankan secara manual:
```bash
pip install -r requirements.txt
python3 server.py
```

#### Menjalankan di Background (PM2 / Daemon):
Jika Anda ingin server tetap berjalan di latar belakang tanpa harus membuka terminal:
```bash
# Menjalankan server
pm2 start server.py --name digikeyboard --interpreter python3

# Melihat status & log
pm2 status digikeyboard
pm2 logs digikeyboard

# Menghentikan server
pm2 stop digikeyboard
```

#### Di Windows:
Cukup klik ganda (double-click) berkas:
```cmd
run.bat
```

---

### 📱 Cara Terhubung dari HP / Tablet
1. Saat server PC aktif, terminal akan menampilkan URL dan QR Code, contoh:
   ```text
   http://192.168.8.103:8080
   ```
2. Buka kamera HP untuk scan **QR Code**, ATAU ketik alamat IP tersebut di browser (Chrome / Safari / Firefox).
3. **Tips Penggunaan Terbaik:**
   - Putar HP ke posisi **Landscape (Mendatar)**.
   - Tekan ikon **⛶ (Fullscreen)** di pojok kanan atas layar agar tampilan keyboard penuh tanpa terhalang toolbar browser.

---

### 🔥 Pemecahan Masalah (Troubleshooting)
* **HP tidak bisa membuka halaman web:**
  Pastikan port 8080 diizinkan pada firewall PC Anda:
  ```bash
  # Ubuntu / Debian
  sudo ufw allow 8080/tcp

  # Fedora / RHEL
  sudo firewall-cmd --add-port=8080/tcp --permanent && sudo firewall-cmd --reload
  ```
* **Karakter tidak terketik di Linux:**
  Pastikan display server X11 aktif (default desktop Ubuntu/Debian). Jika menjalankan melalui SSH, pastikan `export DISPLAY=:0` atau `DISPLAY=:1` sudah ditentukan.

---

## 🇬🇧 English

### 🌟 Overview
Most remote keyboard applications rely on native text inputs that trigger clumsy mobile virtual keyboards (Gboard/SwiftKey), concealing essential PC keys such as **Esc, Tab, Function keys (F1-F12), Alt, Windows/Super, and Arrows**.

**DigiKeyboard** solves this by projecting an authentic, full-fidelity mechanical PC keyboard layout directly onto your mobile browser canvas via low-latency WebSocket communication (1-5 ms).

---

### ⚡ Quick Start
1. Ensure both your PC and mobile device are on the **same local Wi-Fi**.
2. Run on Linux:
   ```bash
   chmod +x install-linux.sh && ./install-linux.sh
   ```
3. Run on Windows:
   Double-click `run.bat`.
4. Scan the terminal ASCII QR code or visit `http://<PC_IP>:8080` in your mobile browser.

---

## 📚 Dokumentasi Lanjutan / Extended Documentation

Seluruh dokumentasi teknis, roadmap produk, dan panduan komersialisasi tersedia di folder [`docs/`](docs/):

* 📐 **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md):** Arsitektur sistem internal, diagram Mermaid, protokol payload WebSocket, dan smart network discovery logic.
* 🗺️ **[docs/ROADMAP.md](docs/ROADMAP.md):** Rencana rilis fitur masa depan (PWA, Virtual Touchpad, 4-digit PIN Pairing, Macro Deck).
* 💼 **[docs/COMMERCIAL_GUIDE.md](docs/COMMERCIAL_GUIDE.md):** Analisis pasar, alternatif branding (*AirDeck*, *DeskPilot*, *TapDeck*), strategi monetisasi (SaaS/Freemium vs Hardware Dongle), dan model penetapan harga.
* 📝 **[CHANGELOG.md](CHANGELOG.md):** Riwayat catatan rilis dan log perubahan lengkap aplikasi.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
