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
   - **Opsi Nyala/Mati (On/Off Toggle):** Trackpad dapat dinonaktifkan sepenuhnya jika tidak dibutuhkan, baik melalui tombol cepat toolbar (`🖱️ Pad`), tombol palm rest (`✕ Matikan Pad`), maupun menu Pengaturan (`🟢 Aktif` / `⚪ Nonaktif`). Status tersimpan permanen.
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
   - **Dukungan PWA (Progressive Web App):** Dilengkapi Web App Manifest (`manifest.json`), Service Worker (`sw.js`), dan opsi instalasi ke Layar Utama (*Home Screen*). Membuka aplikasi secara mandiri (*standalone/fullscreen*) tanpa bilah URL browser dan tanpa popup peringatan fullscreen Chrome.
6. **Mode Penguncian Modifier Persisten (Persistent Modifier Lock):**
   - **Operasi Sama Persis Keyboard Fisik:** Mengetuk tombol `Shift`, `Ctrl`, `Alt`, atau `Win`/`Cmd` akan membuatnya **aktif terus secara mandiri** (tetap tertahan di level driver OS PC) sampai diketuk kembali untuk melepasnya.
   - **Seleksi Teks & Navigasi Lancar:** Memungkinkan seleksi baris berkali-kali (`Shift + ⬇️ + ⬇️ + ⬇️`), navigasi jendela aplikasi (`Alt + Tab + Tab`), pengetikan huruf kapital / simbol beruntun tanpa lepas, dan kombinasi shortcut kompleks.
   - **Pilihan 3 Mode Fleksibel:**
     - `🔒 Lock` (Aktif Terus / Bawaan): Tetap aktif sampai ditekan lagi.
     - `⚡ 1-Shot`: Lepas otomatis setelah 1 tombol berikutnya ditekan.
     - `🖐️ Hold`: Hanya aktif selama jari menyentuh tombol di layar (multi-touch manual).
   - Dapat diubah instan melalui tombol toolbar atas (`🔒 Lock`) maupun menu Pengaturan (⚙️).
7. **Sistem Pemulihan Mandiri Koneksi Wi-Fi (Self-Healing Network & Auto-Reconnect):**
   - **Watchdog Heartbeat & Dead Socket Destroyer:** Menghancurkan socket TCP zombie secara otomatis dalam 5.5 detik saat router Wi-Fi di-restart (mencegah koneksi gantung/hang).
   - **Reconnection Loop Cerdas:** Algoritma exponential backoff dengan jitter acak serta responsivitas instan saat sinyal Wi-Fi terhubung kembali (`online`) dan saat HP dinyalakan dari mode tidur (`visibilitychange`).
   - **Asisten Pemulihan & Pemindai Subnet Otomatis (DHCP IP Change Discovery):** Memindai seluruh subnet lokal pada port 8080 secara paralel dan resolusi nama mDNS (`Jarvis.local`) untuk mendeteksi otomatis jika router memberikan IP baru ke PC setelah reboot.
8. **Smart LAN Detection & QR Code:**
   - Secara otomatis mendeteksi alamat IP Wi-Fi lokal fisik Anda (mengabaikan interface VPN/Docker seperti Cloudflare WARP), dan menampilkan QR code di terminal PC untuk koneksi instan.

---

### 🚀 Cara Menjalankan

#### Persyaratan
- PC dan HP/Tablet terhubung ke **jaringan Wi-Fi yang sama**.
- Python 3.8 atau lebih baru.

#### 1. Di Windows:
Cukup klik ganda (double-click) berkas:
```cmd
run.bat
```
*Script otomatis mendeteksi launcher Python, memasang dependencies (`aiohttp`, `pynput`, `qrcode`), dan menjalankan server.*

#### 2. Di Linux (Ubuntu, Debian, Fedora, Arch):
- **Opsi Utama (Direkomendasikan untuk Dukungan Layar Login, Lock Screen & Sudo Password):**
  ```bash
  chmod +x setup-uinput.sh
  ./setup-uinput.sh
  ```
- **Atau jalankan manual via script runner:**
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

#### 3. Di macOS:
```bash
chmod +x run.sh
./run.sh
```
> *Catatan macOS:* Berikan izin Accessibility untuk aplikasi Terminal/iTerm Anda di **System Settings > Privacy & Security > Accessibility**.

#### Menjalankan di Background (Linux Systemd / PM2):
Untuk menjalankan DigiKeyboard sebagai background daemon permanen saat komputer menyala:
```bash
# Systemd Service (Otomatis aktif sebelum login):
sudo systemctl enable --now digikeyboard.service

# Atau menggunakan PM2:
pm2 start server.py --name digikeyboard --interpreter python3
```

---

### 📱 Cara Terhubung dari HP / Tablet (Android & iOS)

1. Saat server PC aktif, terminal akan menampilkan URL dan QR Code, contoh:
   ```text
   http://192.168.8.103:8080
   ```
2. Buka kamera HP untuk scan **QR Code**, ATAU ketik alamat IP tersebut di browser (Chrome / Safari / Firefox / Edge).
3. **Tips Penggunaan Terbaik:**
   - **Android:** Buka menu browser > ketuk **"Install App"** atau **"Add to Home Screen"** untuk pengalaman keyboard layar penuh (PWA) tanpa address bar.
   - **iOS (iPhone / iPad):** Buka Safari > ketuk tombol **Share (Bagikan)** > pilih **"Add to Home Screen"**. Buka ikon DigiKeyboard dari Home Screen untuk mode Fullscreen native dengan adaptasi notch/island & home bar.
   - Putar perangkat ke posisi **Landscape (Mendatar)**.

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
  Di Windows, klik "Allow Access" jika muncul dialog Windows Defender Firewall.
* **Karakter tidak terketik di Linux:**
  Jalankan `./setup-uinput.sh` untuk menggunakan driver kernel hardware uinput yang mendukung pengetikan di semua aplikasi, terminal, dan kolom password.

---

## 🇬🇧 English

### 🌟 Overview
Most remote keyboard applications rely on native text inputs that trigger clumsy mobile virtual keyboards (Gboard/SwiftKey), concealing essential PC keys such as **Esc, Tab, Function keys (F1-F12), Alt, Windows/Super, and Arrows**.

**DigiKeyboard** solves this by projecting an authentic, full-fidelity mechanical PC keyboard layout directly onto your mobile browser canvas via low-latency WebSocket communication (1-5 ms).

### ✨ Key Features
- **True 1:1 PC Keyboard Canvas:** Number row, full QWERTY, navigation keys, latching modifiers, and Numpad without mobile OS keyboard popup.
- **Laptop Trackpad / Mouse Control Deck:** Smooth multi-touch trackpad with 1-finger left click tap, 2-finger right click tap, 2-finger vertical scroll, physical left/right buttons, position toggle (top/bottom), sizing/sensitivity controls, and persistent On/Off option (via toolbar, palm rest button, or Settings).
- **Tactile & Audio Feedback:** Web Vibration API haptics (Soft, Normal, Strong) and synthesized mechanical switch sound with custom volume slider (10%-100%) and quick presets.
- **Target OS Profile & Layout Selector:** Dedicated OS selector (**Windows**, **macOS**, **Ubuntu / Linux**). Automatically configures physical modifier keys (`control ⌃`, `option ⌥`, `⌘ cmd` on Mac vs `Ctrl`, `⊞ Win`, `Alt` on Windows/Ubuntu), native OS typography, and OS-tailored shortcut bars (`⌘+C`, `⌘+Tab`, `⌘+Space`, `⌥+⌘+Esc` on Mac; `Ctrl+Alt+T` on Ubuntu).
- **Theme & Ergonomics Studio:** Independent visual themes (Native OS, Dark Modern, Retro 90s, Cyberpunk, Stealth, Nord) and granular key height scaling.
- **Independent Font & Typography Studio:** Custom font selector offering 10 distinct font families if you prefer a different look from the theme default (Theme Default/Auto, Ubuntu, Segoe UI, SF Pro Apple, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, System UI).
- **Progressive Web App (PWA) & Zero-Popup Fullscreen:** Add to Home Screen support with Web App Manifest (`manifest.json`), Service Worker (`sw.js`), and high-res app icons for a native full-screen experience with no browser URL bar and no Chrome fullscreen popups.
- **Persistent Modifier Lock (Physical Keyboard Parity):** Modifier keys (`Shift`, `Ctrl`, `Alt`, `Win`/`Cmd`) remain actively held down on the host OS until tapped again, enabling seamless multi-line text selection (`Shift + Arrow + Arrow`), window switching (`Alt + Tab + Tab`), continuous uppercase/symbol typing, and complex desktop shortcuts. Features 3 selectable behaviors: `🔒 Lock` (Persistent), `⚡ 1-Shot` (Auto-release), and `🖐️ Hold` (Touch-and-hold).
- **Self-Healing Wi-Fi Connection & Dynamic IP Discovery:** Heartbeat watchdog destroying zombie sockets in 5.5s upon router reboot, jittered exponential backoff auto-reconnect, network & screen-wake event listeners, and parallel subnet scanner on port 8080 to auto-locate newly assigned PC IP addresses.
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
