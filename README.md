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
2. **Laptop Trackpad / Mouse Control Deck:**
   - Permukaan multitouch trackpad laptop virtual responsif dengan efek visual glow dinamis.
   - **Gesture Multi-Touch:** Geser 1 jari untuk kursor mouse, 1-finger tap untuk Klik Kiri, 2-finger tap untuk Klik Kanan, 2-finger scroll untuk menggulir halaman.
   - **Tombol Fisik Klik:** Tombol Klik Kiri dan Klik Kanan terdedikasi di bawah trackpad.
   - **Posisi Fleksibel:** Bisa dipasang di **Atas** keyboard atau di **Bawah** keyboard sesuai kenyamanan jari.
   - **Kustomisasi Ukuran & Sensitivitas:** Preset ukuran (Kecil 70%, Normal 100%, Besar 130%, Ekstra 160%), slider skala granular (60% - 180%), dan pengatur sensitivitas kursor (0.5x - 3.0x).
3. **Umpan Balik Taktil (Haptic & Audio):**
   - **Haptic Vibration (Getar):** Pilihan preset Lembut (15ms), Normal (30ms), Kuat (50ms), serta tombol uji coba langsung.
   - **Suara Klik Mekanikal Sintetis:** Menghasilkan klik switch mekanik renyah via Web Audio API, terdengar jelas di speaker kecil HP, tablet, maupun PC.
   - **Pengontrol Volume Suara:** Slider granular (10% - 100%), preset Pelan (30%), Sedang (70%), Keras (100%), dan tombol uji suara (`🧪 Uji Suara Klik`).
4. **Panel Ekstensi (Bisa di-toggle):**
   - **Fn Bar:** Tombol `Esc`, `F1` s/d `F12`.
   - **Nav Bar:** `Insert`, `Delete`, `Home`, `End`, `Page Up`, `Page Down`, `Print Screen`.
   - **PC Numpad:** Blok 17 tombol kalkulator angka lengkap.
   - **Shortcut Cepat:** Tombol 1-tap untuk `Ctrl+C`, `Ctrl+V`, `Ctrl+Z`, `Ctrl+A`, `Alt+Tab`, `Win+D`.
5. **Kustomisasi Sistem Operasi, Tema & Font (Menu Pengaturan ⚙️):**
   - **Pemilih Sistem Operasi Terpisah (Target OS):** Pilihan profil OS tersendiri (**Windows**, **macOS**, **Ubuntu / Linux**). Mengubah susunan tuts modifier (misal `control ⌃`, `option ⌥`, `⌘ cmd` pada Mac vs `Ctrl`, `⊞ Win`, `Alt` pada Windows/Ubuntu), font default OS, serta bilah pintasan cepat secara otomatis (`⌘+C`, `⌘+Tab`, `⌘+Space`, `⌥+⌘+Esc` untuk Mac; `Ctrl+Alt+T` untuk Ubuntu).
   - **Koleksi Tema Visual:** Tema Sesuai OS (Native), Dark Modern, Retro 90s, Cyberpunk, Stealth Matte, dan Nord Arctic.
   - **Pemilih Font / Tipografi Mandiri (Custom Typography Studio):** Pilihan 10 jenis font tuts independen jika tidak menyukai font bawaan tema (Bawaan Tema/Auto, Ubuntu, Segoe UI, SF Pro Apple, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, Sistem UI).
   - **Ukuran Tinggi Tombol:** Preset (Kecil, Normal, Besar, Ekstra) dan slider ketinggian tombol (30px - 60px).
   - **Fullscreen & Tip Toggle:** Tombol manual fullscreen (`⛶`) dan opsi sembunyikan baris tip.
6. **Smart LAN Detection & QR Code:**
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

### ✨ Key Features
- **True 1:1 PC Keyboard Canvas:** Number row, full QWERTY, navigation keys, latching modifiers, and Numpad without mobile OS keyboard popup.
- **Laptop Trackpad / Mouse Control Deck:** Smooth multi-touch trackpad with 1-finger left click tap, 2-finger right click tap, 2-finger vertical scroll, physical left/right buttons, position toggle (top/bottom), and sizing/sensitivity controls.
- **Tactile & Audio Feedback:** Web Vibration API haptics (Soft, Normal, Strong) and synthesized mechanical switch sound with custom volume slider (10%-100%) and quick presets.
- **Target OS Profile & Layout Selector:** Dedicated OS selector (**Windows**, **macOS**, **Ubuntu / Linux**). Automatically configures physical modifier keys (`control ⌃`, `option ⌥`, `⌘ cmd` on Mac vs `Ctrl`, `⊞ Win`, `Alt` on Windows/Ubuntu), native OS typography, and OS-tailored shortcut bars (`⌘+C`, `⌘+Tab`, `⌘+Space`, `⌥+⌘+Esc` on Mac; `Ctrl+Alt+T` on Ubuntu).
- **Theme & Ergonomics Studio:** Independent visual themes (Native OS, Dark Modern, Retro 90s, Cyberpunk, Stealth, Nord) and granular key height scaling.
- **Independent Font & Typography Studio:** Custom font selector offering 10 distinct font families if you prefer a different look from the theme default (Theme Default/Auto, Ubuntu, Segoe UI, SF Pro Apple, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, System UI).
- **Instant Connect:** Automatic LAN IP detection and terminal ASCII QR code.

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
