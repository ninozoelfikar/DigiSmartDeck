# ⌨️ DigiSmartDeck (Remote PC Keyboard)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v1.17.0-brightgreen.svg)](CHANGELOG.md)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS%20%7C%20Android-informational)](#)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](#)
[![Tech](https://img.shields.io/badge/Stack-WebSocket%20%7C%20Bluetooth%20HID%20%7C%20aiohttp%20%7C%20uinput-orange.svg)](#)

> **Ubah layar HP / Tablet Anda menjadi keyboard fisik standar PC nirkabel via Wi-Fi lokal atau Bluetooth HID, tanpa memicu keyboard virtual HP bawaan.**  
> *Transform your smartphone or tablet into a full-fidelity wireless PC physical keyboard over local Wi-Fi or Bluetooth HID, without triggering native mobile on-screen keyboards.*

---

*Read in: [Bahasa Indonesia](#-bahasa-indonesia) | [English](#-english)*

---

## 🇮🇩 Bahasa Indonesia

### 🌟 Mengapa DigiSmartDeck?
Mayoritas aplikasi remote keyboard menampilkan kotak teks yang memunculkan keyboard bawaan HP (Gboard / SwiftKey). Hal ini menyulitkan akses ke tombol-tombol fungsional PC seperti **Esc, Tab, Ctrl, Alt, Win/Super, F1-F12, Backspace, Panah**, hingga **Numpad**.

**DigiSmartDeck** menyajikan antarmuka visual layout keyboard fisik PC sesungguhnya langsung di layar HP/Tablet Anda dengan latensi ultra-rendah (1-5 ms) melalui WebSocket Wi-Fi lokal atau emulasi perangkat keras Bluetooth HID.

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
4. **🛡️ Anti-Collision Controller Arbitration (Anti-Tabrakan Pengendali):**
   - **Mencegah Tabrakan Multi-User:** Jika beberapa HP atau tablet membuka URL DigiSmartDeck secara bersamaan di jaringan yang sama, sistem arbitrase memastikan hanya 1 perangkat yang menjadi **Pengendali Aktif** (`🟢 👑 Pengendali Aktif`).
   - **Mode Siaga Otomatis (Standby):** Perangkat lain yang terhubung otomatis masuk ke mode `🟡 ⚡ Siaga (Ambil Alih)` dengan pengetikan diabaikan server agar tidak mengacaukan sesi yang sedang berjalan.
   - **Pengambilan Alih Instan (Takeover):** Pengguna di mode siaga dapat mengetuk tombol status untuk mengambil alih kendali dengan konfirmasi 1-ketuk.
   - **Auto-Takeover:** Mengalihkan kendali secara otomatis jika pengendali aktif tidak melakukan pengetikan selama 30 detik.
   - **Pelepasan Modifier Bersih:** Saat handoff atau putus koneksi, seluruh tombol modifier yang tertahan (Shift, Ctrl, Alt, Win) otomatis dilepas di level OS.
5. **📱 Aplikasi Android Native (APK Langsung Download):**
   - Mengatasi batasan browser mobile Chrome (*"This app cannot be installed"* pada HTTP lokal dan peringatan popup fullscreen yang mengganggu).
   - Menghadirkan *True Immersive Sticky Fullscreen*, rotasi lanskap terkunci otomatis, dan layar tetap menyala (*keep screen awake*).
   - Dapat diunduh langsung dari halaman server: `http://<PC_IP>:8080/download/apk` atau tombol unduh di browser.
6. **📶 Opsi Koneksi Ganda (Wi-Fi WebSocket + Bluetooth HID):**
   - **Jalur Wi-Fi WebSocket:** Latensi ultra-rendah 1–5 ms melalui jaringan lokal tanpa konfigurasi khusus.
   - **Jalur Bluetooth HID Hardware Emulation (Android):** Emulasi standar Keyboard + Mouse Bluetooth hardware menggunakan `BluetoothHidDevice` (Android 9+). Terhubung langsung ke PC Windows, Mac, iPad, atau Smart TV tanpa perlu menginstal aplikasi server apa pun di perangkat penerima!
7. **Panel Ekstensi (Bisa di-toggle):**
   - **Fn Bar:** Tombol `Esc`, `F1` s/d `F12`.
   - **Nav Bar:** `Insert`, `Delete`, `Home`, `End`, `Page Up`, `Page Down`, `Print Screen`.
   - **PC Numpad:** Blok 17 tombol kalkulator angka lengkap.
   - **Shortcut Cepat:** Tombol 1-tap untuk `Ctrl+C`, `Ctrl+V`, `Ctrl+Z`, `Ctrl+A`, `Alt+Tab`, `Win+D`.
8. **Kustomisasi Sistem Operasi, Tema & Font (Menu Pengaturan ⚙️):**
   - **Pemilih Sistem Operasi Terpisah (Target OS):** Pilihan profil OS tersendiri (**Windows**, **macOS**, **Ubuntu / Linux**). Mengubah susunan tuts modifier (misal `control ⌃`, `option ⌥`, `⌘ cmd` pada Mac vs `Ctrl`, `⊞ Win`, `Alt` pada Windows/Ubuntu), font default OS, serta bilah pintasan cepat secara otomatis (`⌘+C`, `⌘+Tab`, `⌘+Space`, `⌥+⌘+Esc` untuk Mac; `Ctrl+Alt+T` untuk Ubuntu).
   - **Koleksi Tema Visual:** Tema Sesuai OS (Native), Dark Modern, Retro 90s, Cyberpunk, Stealth Matte, dan Nord Arctic.
   - **Pemilih Font / Tipografi Mandiri (Custom Typography Studio):** Pilihan 10 jenis font tuts independen jika tidak menyukai font bawaan tema (Bawaan Tema/Auto, Ubuntu, Segoe UI, SF Pro Apple, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, Sistem UI).
   - **Ukuran Tinggi Tombol:** Preset (Kecil, Normal, Besar, Ekstra) dan slider ketinggian tombol (30px - 60px).
   - **Fullscreen & Tip Toggle:** Tombol manual fullscreen (`⛶`) dan opsi sembunyikan baris tip.
   - **Dukungan PWA (Progressive Web App):** Dilengkapi Web App Manifest (`manifest.json`), Service Worker (`sw.js`), dan opsi instalasi ke Layar Utama (*Home Screen*).
9. **Mode Penguncian Modifier Persisten (Persistent Modifier Lock):**
   - **Operasi Sama Persis Keyboard Fisik:** Mengetuk tombol `Shift`, `Ctrl`, `Alt`, atau `Win`/`Cmd` akan membuatnya **aktif terus secara mandiri** (tetap tertahan di level driver OS PC) sampai diketuk kembali untuk melepasnya.
   - **Seleksi Teks & Navigasi Lancar:** Memungkinkan seleksi baris berkali-kali (`Shift + ⬇️ + ⬇️ + ⬇️`), navigasi jendela aplikasi (`Alt + Tab + Tab`), pengetikan huruf kapital / simbol beruntun tanpa lepas, dan kombinasi shortcut kompleks.
   - **Pilihan 3 Mode Fleksibel:** `🔒 Lock` (Aktif Terus / Bawaan), `⚡ 1-Shot` (Lepas otomatis setelah 1 tombol berikutnya ditekan), `🖐️ Hold` (Hanya aktif selama jari menyentuh layar).
10. **Sistem Pemulihan Mandiri Koneksi Wi-Fi (Self-Healing Network & Auto-Reconnect):**
    - **Watchdog Heartbeat & Dead Socket Destroyer:** Menghancurkan socket TCP zombie secara otomatis dalam 5.5 detik saat router Wi-Fi di-restart (mencegah koneksi gantung/hang).
    - **Reconnection Loop Cerdas:** Algoritma exponential backoff dengan jitter acak serta responsivitas instan saat sinyal Wi-Fi terhubung kembali (`online`) dan saat HP dinyalakan dari mode tidur (`visibilitychange`).
    - **Asisten Pemulihan & Pemindai Subnet Otomatis (DHCP IP Change Discovery):** Memindai seluruh subnet lokal pada port 8080 secara paralel dan resolusi nama mDNS (`Jarvis.local`) untuk mendeteksi otomatis jika router memberikan IP baru ke PC setelah reboot.
11. **🛠️ Pemeriksa Sistem Pra-Jalan Cerdas (System Pre-Flight Checker):**
    - Otomatis mengecek kesehatan port, firewall, dan izin kernel sebelum server berjalan via `system_checker.py`.
    - Menangani bentrokan port 8080 secara ramah tanpa crash atau pesan traceback yang membingungkan orang awam.
12. **Smart LAN Detection & QR Code:**
    - Secara otomatis mendeteksi alamat IP Wi-Fi lokal fisik Anda (mengabaikan interface VPN/Docker seperti Cloudflare WARP), dan menampilkan QR code di terminal PC untuk koneksi instan.
13. **📽️ Mode Presentasi & Meeting Controller (Workstation Remote):**
    - Mengubah HP menjadi remote slide profesional: navigasi raksasa `NEXT ➡` & `PREV ⬅`, tombol layar hitam (`B`), layar putih (`W`), laser pointer (`Ctrl+L`), spidol coret (`Ctrl+P`), dan penghapus (`E`).
    - Dilengkapi **Digital Countdown Timer** dengan alarm getar hening (*silent haptic feedback*), mini touchpad laser, serta sensor **Air Mouse (Gyro Pointer)** untuk mengarahkan kursor dengan memiringkan HP.
    - Tombol cepat meeting online (Zoom, Google Meet, Microsoft Teams): Toggle Mute Mikrofon, Kamera Video, Angkat Tangan (*Raise Hand*), dan Bagikan Layar (*Share Screen*).
14. **🎮 Mode Game Console (Virtual Gamepad):**
    - Gamepad virtual layar penuh dengan D-Pad kinetik 8-arah atau Virtual Thumbstick, tombol aksi berlian `A/B/X/Y`, tombol bahu `L1/R1`, dan analog triggers `L2/R2`.
    - Preset siap pakai: RetroArch/SNES, GBA, PlayStation (PSX/PCSX2), dan Modern PC WASD dengan modal remap kustom mandiri.
15. **Keamanan & Privasi Mutlak (Zero-Telemetry & 100% On-Premise):**
    - **Nol Perekaman Ketikan (Zero Keystroke Logging):** Input pengetikan, password, dan suara dieksekusi seketika ke kernel OS dan tidak pernah disimpan ke file log, disk, maupun cloud.
    - **100% On-Premise (Air-Gapped Ready):** Beroperasi murni di jaringan lokal (Wi-Fi atau kabel USB offline) tanpa pelacak analitik pihak ketiga.
    - **Proteksi PIN Fisik 6-Digit & Anti Brute-Force:** Hanya perangkat dengan PIN fisik dari layar PC yang dapat mengendalikan, diperkuat mitigasi brute-force bertingkat dan isolasi localhost pada endpoint kontrol sensitif.

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
Untuk menjalankan DigiSmartDeck sebagai background daemon permanen saat komputer menyala:
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
   http://192.168.8.100:8080
   ```
2. Buka kamera HP untuk scan **QR Code**, ATAU ketik alamat IP tersebut di browser (Chrome / Safari / Firefox / Edge).
3. **Pilihan Cara Menggunakan:**
   - **📱 Aplikasi Android Native (Direkomendasikan untuk Pengalaman Terbaik):**
     - Buka `http://<PC_IP>:8080/download/apk` di browser HP atau klik tombol **"📱 Download Android APK"** di header web.
     - Pasang APK `DigiSmartDeck.apk` di HP Anda.
     - Nikmati fullscreen murni tanpa popup peringatan Chrome, orientasi landscape terkunci, dan opsi **Bluetooth HID**.
   - **🌐 Mode Web Browser / PWA:**
     - **Android:** Buka menu Chrome > ketuk **"Add to Home Screen"** / **"Install App"**.
     - **iOS (iPhone / iPad):** Buka Safari > ketuk tombol **Share (Bagikan)** > pilih **"Add to Home Screen"**.
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

**DigiSmartDeck** solves this by projecting an authentic, full-fidelity mechanical PC keyboard layout directly onto your mobile canvas via low-latency WebSocket communication (1-5 ms) or direct Bluetooth HID hardware emulation.

### ✨ Key Features
- **True 1:1 PC Keyboard Canvas:** Number row, full QWERTY, navigation keys, latching modifiers, and Numpad without mobile OS keyboard popup.
- **Laptop Trackpad / Mouse Control Deck:** Smooth multi-touch trackpad with 1-finger left click tap, 2-finger right click tap, 2-finger vertical scroll, physical left/right buttons, position toggle (top/bottom), sizing/sensitivity controls, and persistent On/Off option (via toolbar, palm rest button, or Settings).
- **Tactile & Audio Feedback:** Web Vibration API haptics (Soft, Normal, Strong) and synthesized mechanical switch sound with custom volume slider (10%-100%) and quick presets.
- **🛡️ Anti-Collision Controller Arbitration:** Prevents keystroke interleaving and pointer jitter when multiple family members or devices open the keyboard simultaneously. Automatically designates one Active Controller (`🟢 👑 Active Controller`) while placing other devices into Standby Mode (`🟡 ⚡ Standby (Takeover)`). Features 1-tap takeover, 30s idle auto-takeover, and clean modifier release on handoff/disconnect.
- **📱 Android Native Client (Direct APK Download):** Bypasses browser PWA/fullscreen limitations, offering true sticky immersive fullscreen, locked landscape, screen keep-awake, and direct download from `http://<PC_IP>:8080/download/apk`.
- **📶 Dual Wireless Modes (Wi-Fi + Bluetooth HID):** Connect via high-speed local Wi-Fi WebSocket or switch to native Bluetooth HID hardware emulation (Keyboard + Mouse composite device) to control PCs, Macs, iPads, or Smart TVs without installing server software.
- **Target OS Profile & Layout Selector:** Dedicated OS selector (**Windows**, **macOS**, **Ubuntu / Linux**). Automatically configures physical modifier keys (`control ⌃`, `option ⌥`, `⌘ cmd` on Mac vs `Ctrl`, `⊞ Win`, `Alt` on Windows/Ubuntu), native OS typography, and OS-tailored shortcut bars (`⌘+C`, `⌘+Tab`, `⌘+Space`, `⌥+⌘+Esc` on Mac; `Ctrl+Alt+T` on Ubuntu).
- **Theme & Ergonomics Studio:** Independent visual themes (Native OS, Dark Modern, Retro 90s, Cyberpunk, Stealth, Nord) and granular key height scaling.
- **Independent Font & Typography Studio:** Custom font selector offering 10 distinct font families if you prefer a different look from the theme default (Theme Default/Auto, Ubuntu, Segoe UI, SF Pro Apple, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, System UI).
- **Progressive Web App (PWA) & Zero-Popup Fullscreen:** Add to Home Screen support with Web App Manifest (`manifest.json`), Service Worker (`sw.js`), and high-res app icons for a native full-screen experience.
- **Persistent Modifier Lock (Physical Keyboard Parity):** Modifier keys (`Shift`, `Ctrl`, `Alt`, `Win`/`Cmd`) remain actively held down on the host OS until tapped again, enabling seamless multi-line text selection (`Shift + Arrow + Arrow`), window switching (`Alt + Tab + Tab`), continuous uppercase/symbol typing, and complex desktop shortcuts. Features 3 selectable behaviors: `🔒 Lock` (Persistent), `⚡ 1-Shot` (Auto-release), and `🖐️ Hold` (Touch-and-hold).
- **Self-Healing Wi-Fi Connection & Dynamic IP Discovery:** Heartbeat watchdog destroying zombie sockets in 5.5s upon router reboot, jittered exponential backoff auto-reconnect, network & screen-wake event listeners, and parallel subnet scanner on port 8080 to auto-locate newly assigned PC IP addresses.
- **🛠️ System Pre-Flight Diagnostics:** Non-technical friendly preflight audit (`system_checker.py`) gracefully handling port 8080 conflicts, Linux `/dev/uinput` permissions, and firewalls without panic tracebacks.
- **📽️ Presentation & Meeting Remote Mode:** Oversized 1-tap `NEXT ➡` and `PREV ⬅` keys, blank/black screen (`B`), white screen (`W`), laser pointer (`Ctrl+L`), and pen annotations (`Ctrl+P`). Features a digital countdown timer with silent haptic reminder alerts, mini laser trackpad, and motion-based **Gyro Air Pointer** (tilt smartphone to aim). Includes 1-tap online meeting controls for Zoom, Google Meet, and Microsoft Teams (Mute, Video, Raise Hand, Screen Share).
- **🎮 Game Console Mode (Virtual Gamepad):** Full-screen touch gamepad featuring an 8-way kinetic D-Pad or Virtual Thumbstick, diamond action buttons (`A/B/X/Y`), shoulder bumpers (`L1/R1`), and analog triggers (`L2/R2`). Built-in presets for RetroArch, GBA, PlayStation, and Modern PC WASD with custom remapping modal.
- **📦 Standalone Portable Executables:** Ready-to-run binaries without manual Python setup for Linux (`dist/DigiSmartDeck`), Windows (`dist/DigiSmartDeck.exe`), and macOS (`dist/DigiSmartDeckApp.app`).
- **Instant Connect:** Automatic LAN IP detection and terminal ASCII QR code.

---

### ⚡ Quick Start
1. Ensure both your PC and mobile device are on the **same local Wi-Fi**.
2. Run on Linux:
   ```bash
   chmod +x install-linux.sh && ./install-linux.sh
   # Or run the standalone executable:
   ./dist/DigiSmartDeck
   ```
3. Run on Windows:
   Double-click `run.bat` or run `dist\DigiSmartDeck.exe`.
4. Scan the terminal ASCII QR code or visit `http://<PC_IP>:8080` in your mobile browser, or download `http://<PC_IP>:8080/download/apk` on Android.

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
