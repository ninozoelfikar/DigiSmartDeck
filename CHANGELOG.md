# 📝 Changelog / Catatan Perubahan DigiKeyboard

Semua perubahan penting pada proyek **DigiKeyboard** dicatat dalam berkas ini.  
Format penulisan mengacu pada [Keep a Changelog](https://keepachangelog.com/id/1.0.0/) dan mengikuti standar [Semantic Versioning](https://semver.org/).

*Read in: [Bahasa Indonesia](#-bahasa-indonesia) | [English](#-english)*

---

## 🇮🇩 Bahasa Indonesia

### [1.15.0] - 2026-09-26
- Sistem pemulihan mandiri koneksi Wi-Fi (watchdog 5.5s, auto-reconnect backoff, dan pemindai subnet deteksi IP baru PC)

### [1.14.0] - 2026-09-26
- Implementasi Progressive Web App (PWA) dengan manifest.json, sw.js, dan icon HD untuk mode fullscreen bebas popup Chrome

### [1.13.0] - 2026-09-26
- Penambahan opsi matikan trackpad laptop (On/Off Toggle) via Pengaturan, toolbar, dan palm rest

### [1.12.1] - 2026-09-26
- Penyempurnaan auto-detect host OS, insets viewport mobile, dan key aliases

### [1.12.0] - 2026-09-26
- Penambahan pemilih font keyboard mandiri (Custom Typography Studio) dengan 10 pilihan font

### [1.11.1] - 2026-09-26
- Pemisahan menu profil sistem operasi (Target OS) dan tema visual keyboard tersendiri

### [1.11.0] - 2026-09-26
- Penyesuaian font keyboard per tema dan penambahan tema Windows, Mac, dan Ubuntu

### [1.10.0] - 2026-09-26
- Dukungan Linux kernel uinput untuk pengetikan pada Layar Login Ubuntu (GDM) dan Lock Screen

### [1.9.0] - 2026-09-26
- Menambahkan pengaturan volume suara klik mekanikal (slider & preset) di menu Pengaturan

### [1.8.1] - 2026-09-26
- Optimasi audio feedback klik mekanikal untuk speaker HP dan penambahan tombol uji suara

### [1.8.0] - 2026-09-26
- Menambahkan audio click feedback dan deteksi motor getar perangkat

### [1.7.0] - 2026-09-26
- Pindahkan slider sensitivitas kursor trackpad ke dalam modal Pengaturan

### [1.6.0] - 2026-09-26
- Menambahkan pengaturan efek getar haptic feedback dan pilihan intensitas di modal Settings

### [1.5.2] - 2026-09-26
- Perbaikan isolasi CSS fullscreen tip dan tombol tutup tip langsung

### [1.5.1] - 2026-09-26
- Hilangkan modifier strip atas dan sembunyikan tip otomatis saat fullscreen

### [1.5.0] - 2026-09-26
- Menambahkan pengaturan ukuran & skala tinggi trackpad

### [1.4.1] - 2026-09-26 (Stable Golden Checkpoint)
#### 🛠️ Perbaikan & Stabilitas (Fixed & Stabilized)
- **Perbaikan Critical Syntax Error Client:** Memperbaiki penutupan blok kurung kurawal `}` pada *event listener* trackpad kanan di `static/index.html` yang sempat menyebabkan *parser crash* pada browser HP/Tablet.
- **Pembersihan Fitur Fullscreen Otomatis:** Membatalkan percobaan *auto-fullscreen* dan mengembalikan kendali manual melalui tombol `⛶` demi stabilitas rendering di semua jenis peramban mobile.
- **Sistem Versi Otomatis Terpusat:** Menetapkan berkas `VERSION` sebagai *single source of truth*, integrasi endpoint `/api/version`, serta penambahan lencana versi di modal Pengaturan.
- **Milestone Stabil:** Menetapkan versi `1.4.1` sebagai titik aman optimal terverifikasi (koneksi instan, 5 tema skin, slider ukuran tombol, continuous key repeat, dan trackpad multi-touch).

### [1.4.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Modal Pengaturan Tema & Skin Keyboard:** Menambahkan tombol pengaturan `⚙️` pada toolbar atas dengan 5 tema visual kustom:
  - *Dark Modern*: Tema bawaan bernuansa GitHub Dark / VS Code yang nyaman di mata.
  - *Retro 90s*: Tampilan klasik beige gading khas keyboard IBM Model M tahun 1990-an.
  - *Cyberpunk*: Aksen neon ungu elektrik, garis tepi cyan, dan enter magenta cerah.
  - *Stealth*: Matte black monokrom super gelap dan minimalis untuk pencahayaan rendah.
  - *Nord Arctic*: Palet warna biru beku Arktik Nord yang elegan dan sejuk.
- **Pengatur Ukuran & Skalabilitas Tombol:** Pengguna dapat menyesuaikan tinggi tombol keyboard sesuai kenyamanan jari:
  - Tersedia 4 preset cepat: *Kecil* (32px), *Normal* (38px), *Besar* (46px), dan *Ekstra* (54px).
  - Slider interaktif granular dari `30px` hingga `60px` dengan penskalaan ukuran huruf secara otomatis dan proporsional.
- **Penyimpanan Preferensi (Persistence):** Semua pilihan tema, ukuran tombol, dan orientasi trackpad tersimpan otomatis di *localStorage* browser.

#### 🛠️ Perbaikan & Tata Letak (Fixed & Changed)
- **Kuncian Posisi Baris Fn di Atas Angka:** Memindahkan baris Fn (`Esc`, `F1-F12`) dan baris Navigasi langsung ke dalam kontainer utama keyboard (`.kb-main`), sehingga saat diaktifkan, baris Fn **selalu berada tepat di atas baris angka**, baik ketika trackpad ditaruh di posisi atas maupun di bawah.
- **Sinkronisasi Sakelar Posisi Trackpad:** Opsi pemindahan posisi trackpad di dalam modal pengaturan tersinkronisasi dua arah dengan tombol sakelar di sandaran tangan.

---

### [1.3.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Continuous Key Auto-Repeat:** Menahan tombol keyboard (seperti `Backspace`, `Delete`, panah `▲ ◀ ▼ ▶`, `Space`, huruf/angka) sekarang menghasilkan input berulang otomatis (~22 karakter/detik setelah jeda awal 350ms), persis seperti keyboard fisik PC.
- **Interactive Trackpad Position Switcher:** Tombol sakelar `⇅ Posisi: Atas / Bawah` yang memungkinkan pengguna memindahkan dek trackpad ke atas keyboard atau ke bawah keyboard secara instan tanpa perlu memuat ulang halaman. Preferensi posisi tersimpan di *localStorage*.

#### 🎨 Perubahan Tampilan & Desain (Changed)
- **Penyesuaian Proporsi Trackpad:** Mengurangi tinggi dek trackpad sebesar 30% pada semua ukuran layar (tablet, tablet besar, dan smartphone) agar keyboard mendapatkan porsi ruang yang lebih luas dan ergonomis.
- **Posisi Default di Atas Keyboard:** Menempatkan dek trackpad di bagian atas secara default sesuai preferensi penggunaan meja pada layar sentuh tablet.

---

### [1.2.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Laptop Trackpad Deck:** Penambahan modul trackpad terintegrasi dengan sandaran tangan (*palm rest*) di bawah keyboard layaknya laptop sungguhan.
- **Multi-Touch Gestures:**
  - 1 Jari geser: Gerak kursor mouse kinetik dengan efek visual *glow*.
  - 1 Jari tap: Klik Kiri mouse (+ getaran haptic).
  - 2 Jari tap: Klik Kanan mouse.
  - 2 Jari geser vertikal: Scroll dokumen & web secara halus (*smooth scrolling*).
- **Tombol Fisik Klik Kiri & Kanan:** Tombol perangkat keras virtual di bawah trackpad yang mendukung aksi *drag and drop* (menahan tombol klik kiri sambil menggeser jari di trackpad).
- **Kontrol Sensitivitas Kursor:** Slider pengatur kecepatan kursor mouse (`0.5x` s/d `3.0x`).
- **Integrasi Server Mouse:** Dukungan penuh untuk simulasi `pynput.mouse` (`mousemove`, `mouseclick`, `mousedown`, `mouseup`, `mousescroll`) pada `server.py`.
- **Toggle Button Toolbar:** Tombol `🖱️ Pad` pada toolbar atas untuk menyembunyikan/menampilkan trackpad.

---

### [1.1.0] - 2026-09-26
#### 📚 Dokumentasi & Arsitektur (Added)
- **Dokumentasi Komprehensif Bilingual:**
  - `README.md`: Panduan instalasi modern, background service PM2, dan konfigurasi firewall.
  - `docs/ARCHITECTURE.md`: Diagram sistem Mermaid, spesifikasi protokol WebSocket, dan logika deteksi jaringan.
  - `docs/ROADMAP.md`: Rencana rilis masa depan (PWA, tema estetika mekanikal, audio switch, layout tablet 10-12").
  - `docs/COMMERCIAL_GUIDE.md`: Analisis kompetitor, keunggulan visual *white space*, alternatif branding (*AirDeck*, *DeskPilot*), dan strategi monetisasi.
  - `LICENSE`: Lisensi resmi MIT open-source.

#### 🐛 Perbaikan Bug & Optimasi Jaringan (Fixed)
- **Smart LAN IP Detection:** Mengoptimalkan fungsi `get_local_ip_addresses()` dengan pustaka `psutil` untuk memprioritaskan antarmuka Wi-Fi fisik (`192.168.x.x` / `10.x.x.x`) dan memfilter antarmuka virtual/VPN (Cloudflare WARP, Docker, virbr).
- **QR Code Akurat:** QR code dan URL terminal dipastikan selalu mengarah ke IP Wi-Fi lokal yang dapat diakses oleh HP/Tablet.
- **Dependency Management:** Menambahkan dependensi `aiohttp` yang hilang ke dalam `requirements.txt`.
- **Daemon Support:** Panduan dan kompatibilitas penuh dengan PM2 background process manager.

---

### [1.0.0] - 2026-09-26
#### 🚀 Rilis Awal (Initial Release)
- **1:1 Canvas Physical PC Keyboard:** Tampilan visual keyboard fisik standar PC di browser HP/Tablet tanpa memicu keyboard bawaan smartphone (zero Gboard popup).
- **Layout Standar PC:** Baris angka/simbol Shift, Tab, CapsLock, Enter lebar, Backspace lebar, panah navigasi, dan modifier keys (Ctrl, Alt, Shift, Win/Cmd).
- **Sticky / Latch Modifier Mode:** Mengetuk Ctrl/Alt/Shift mengunci status tombol hingga karakter berikutnya ditekan.
- **Panel Ekstensi:** Panel toggle untuk F1-F12, tombol navigasi (Home, End, PgUp, PgDn, PrtSc, Del), Numpad 17 tombol kalkulator, dan tombol pintasan cepat (Ctrl+C, Ctrl+V, Alt+Tab, Win+D, Ctrl+Alt+Del).
- **Protokol WebSocket Cepat:** Latensi ultra-rendah (1-5 ms) melalui WebSocket server berbasis Python `aiohttp` dan `pynput`.
- **Skrip Installer Linux:** Skrip otomasi `install-linux.sh` dan `run.sh`.

---

## 🇬🇧 English

### [1.15.0] - 2026-09-26
- Release v1.15.0 updates

### [1.14.0] - 2026-09-26
- Release v1.14.0 updates

### [1.13.0] - 2026-09-26
- Release v1.13.0 updates

### [1.12.1] - 2026-09-26
- Release v1.12.1 updates

### [1.12.0] - 2026-09-26
- Release v1.12.0 updates

### [1.11.1] - 2026-09-26
- Release v1.11.1 updates

### [1.11.0] - 2026-09-26
- Release v1.11.0 updates

### [1.10.0] - 2026-09-26
- Release v1.10.0 updates

### [1.9.0] - 2026-09-26
- Release v1.9.0 updates

### [1.8.1] - 2026-09-26
- Release v1.8.1 updates

### [1.8.0] - 2026-09-26
- Release v1.8.0 updates

### [1.7.0] - 2026-09-26
- Release v1.7.0 updates

### [1.6.0] - 2026-09-26
- Release v1.6.0 updates

### [1.5.2] - 2026-09-26
- Release v1.5.2 updates

### [1.5.1] - 2026-09-26
- Release v1.5.1 updates

### [1.5.0] - 2026-09-26
- Release v1.5.0 updates

### [1.4.1] - 2026-09-26 (Stable Golden Checkpoint)
#### Fixed & Stabilized
- **Client Script Syntax Fix:** Resolved missing closing brace `}` inside right trackpad click handler in `static/index.html` which previously prevented browser script execution.
- **Manual Fullscreen Restored:** Completely removed experimental auto-fullscreen, restoring standard manual toggle `⛶` for cross-platform stability.
- **Centralized Automated Versioning:** Introduced `VERSION` file as single source of truth, added `/api/version` endpoint, and integrated version badge in the Settings modal.
- **Golden Milestone:** Verified stable operation with WebSocket connectivity, 5 themes, sizing slider, locked Fn row, continuous key repeat, and multi-touch trackpad.

### [1.4.0] - 2026-09-26
#### Added
- **Settings Modal & Keyboard Themes:** Added a settings button `⚙️` to the header toolbar featuring 5 bespoke visual themes:
  - *Dark Modern*: Default GitHub Dark / VS Code aesthetic.
  - *Retro 90s*: Classic 1990s beige aesthetic inspired by IBM Model M mechanical keyboards.
  - *Cyberpunk*: High-contrast neon purple, cyan glow borders, and hot magenta accents.
  - *Stealth*: Pure matte black and charcoal minimalist style for dark environments.
  - *Nord Arctic*: Frosty Arctic Nord blue palette.
- **Custom Key Sizing & Dynamic Scaling:** Flexible keyboard button height control:
  - 4 one-touch presets: *Compact* (32px), *Normal* (38px), *Large* (46px), and *XL* (54px).
  - Granular slider ranging from `30px` to `60px` with proportional font-size recalculation.
- **Full Client Persistence:** All custom themes, button heights, and trackpad positions persist automatically in browser `localStorage`.

#### Fixed & Changed
- **Locked Fn Bar Placement Above Numbers:** Relocated `#fn-row` (`Esc`, `F1-F12`) and `#nav-row` into `.kb-main` directly above Row 1 numbers, ensuring the Fn row is permanently anchored on top of the number keys regardless of trackpad deck orientation (top or bottom).
- **Two-Way Trackpad Position Sync:** Trackpad orientation controls inside the settings dialog stay seamlessly synced with the deck palm rest toggle.

---

### [1.3.0] - 2026-09-26
#### Added
- **Continuous Key Auto-Repeat:** Holding down keyboard buttons (such as `Backspace`, `Delete`, arrow keys `▲ ◀ ▼ ▶`, `Space`, or letters/numbers) now triggers continuous repeat input (~22 keys/sec after 350ms initial delay), mimicking real physical PC keyboards.
- **Interactive Trackpad Position Switcher:** Added a quick toggle button `⇅ Posisi: Atas / Bawah` in the palm rest to dynamically swap the trackpad deck between the top and bottom of the keyboard without page reloads.

#### Changed
- **Proportional Dimension Tuning:** Reduced trackpad deck height by 30% across all viewports to provide significantly more room for the keyboard keys.
- **Default Top Placement:** Set the trackpad position to the top of the keyboard canvas by default for tablet usage ergonomics.

---

### [1.2.0] - 2026-09-26
#### Added
- **Integrated Laptop Trackpad Deck:** Added an authentic laptop lower deck layout with palm rests and a centered multi-touch trackpad.
- **Multi-Touch Trackpad Gestures:** Single-finger movement, tap-to-click, two-finger right click, and two-finger kinetic vertical scrolling.
- **Physical Left & Right Buttons:** Virtual hardware click pads supporting click-and-drag window selection.
- **Sensitivity Slider:** Adjustable cursor speed control from `0.5x` to `3.0x`.
- **Server Mouse Pipeline:** Full `pynput.mouse` backend event dispatching in `server.py`.
- **Toolbar Toggle:** `🖱️ Pad` button in the header toolbar to hide/show the deck.

---

### [1.1.0] - 2026-09-26
#### Added
- **Complete Bilingual Documentation:** System architecture, WebSocket protocol specs, product roadmap, and commercialization blueprints.
- **MIT License:** Open-source license attribution.

#### Fixed
- **Smart Interface Filtering:** Prioritize reachable physical LAN/Wi-Fi adapters over virtual/VPN adapters (Cloudflare WARP, Docker).
- **Terminal QR Code:** Accurate routing QR code generation.
- **Dependency Tracking:** Added missing `aiohttp` requirement to `requirements.txt`.

---

### [1.0.0] - 2026-09-26
#### Initial Release
- Full PC mechanical keyboard layout rendered on mobile browsers without native IME popups.
- Low-latency Python `aiohttp` WebSocket server and `pynput` input pipeline.
- Sticky/latch modifier keys and multi-finger touch detection.
- Toggle panels for Fn bar (F1-F12), Nav bar, PC Numpad, and quick shortcuts.
