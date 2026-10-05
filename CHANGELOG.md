# 📝 Changelog / Catatan Perubahan DigiSmartDeck

Semua perubahan penting pada proyek **DigiSmartDeck** dicatat dalam berkas ini.  
Format penulisan mengacu pada [Keep a Changelog](https://keepachangelog.com/id/1.0.0/) dan mengikuti standar [Semantic Versioning](https://semver.org/).

*Read in: [Bahasa Indonesia](#-bahasa-indonesia) | [English](#-english)*

---

## Bahasa Indonesia

### [1.19.0] - 2026-10-05
- Penambahan Mode Power untuk kontrol daya dan sesi PC multi-OS

### [1.18.6] - 2026-10-05
- Eliminasi tombol dev bar atas dan modernisasi icon refresh windows PC

### [1.18.5] - 2026-10-05
- Eliminasi total nada beep penutup Google Speech saat mic dimatikan

### [1.18.4] - 2026-10-05
- Sinkronisasi UI APK dan Web identik serta pengembalian redaman nada mic Google Voice

### [1.18.3] - 2026-10-05
- Perbaikan transkripsi berulang dan stabilitas mikrofon

### [1.18.2] - 2026-10-05
- Otomatisasi Always-On Google Voice continuous listening secara default dan eliminasi toggle manual

### [1.18.1] - 2026-10-05
- Perbaikan mic continuous listening: perpanjang silence window, auto-restart tanpa putus seperti Google Voice typing, dan peredam chime

### [1.18.0] - 2026-10-05
- Peluncuran MVP Landing Page dan standarisasi tampilan APK identik dengan Chrome mobile

### [1.17.0] - 2026-09-28
#### ✨ Fitur Baru (Added)
- **Aplikasi Native Android (DigiSmartDeck.apk):**
  - Pembuatan project Android mandiri di folder `android/` berbasis WebView berperforma tinggi dan SDK Android 14.
  - **Mode True Immersive Sticky Fullscreen:** Mengeliminasi seluruh pop-up dan peringatan browser Chrome (*"Swipe down from the top to exit full screen"* dan *"This app cannot be installed"*).
  - Fitur *Auto-Landscape*, *Keep Screen Awake*, dan *Soft Keyboard Suppressed* (mencegah keyboard virtual bawaan HP muncul menutupi tuts).
  - Tautan download instan langsung di server lokal: `http://<IP-PC>:8080/static/DigiSmartDeck.apk` dan tombol 1-klik di modal Pengaturan.
- **Dukungan Bluetooth HID Hardware (Plug & Play Tanpa Server PC):**
  - Implementasi modul `BluetoothHidHelper.java` (Android 9+ API 28) dengan standar USB Composite HID Report Descriptor (Keyboard + Mouse).
  - Menyamarkan HP menjadi keyboard & mouse fisik nirkabel asli yang langsung dikenali oleh Windows, macOS, Linux, iPad, Android TV, bahkan menu BIOS/UEFI tanpa perlu software server di PC.
  - Tombol sakelar cepat `📶 BT` pada toolbar antarmuka pengguna.
- **Sistem Arbitrase Anti-Tabrakan Antar Pengguna (Single Active Controller):**
  - Arbitrase pengendali aktif tunggal di `server.py`: perangkat pertama yang tersambung otomatis menjadi `👑 Pengendali Aktif`.
  - Perangkat kedua atau berikutnya otomatis masuk ke `🟡 Mode Siaga (Standby)` dengan penahanan input di level server guna mencegah benturan tuts (*interleaved typing*) dan perebutan kursor mouse.
  - Tombol `⚡ Ambil Alih (Takeover)` dan *Auto-Takeover* saat pengendali aktif idle > 30 detik.
  - Pelepasan tombol bersih (*Clean Key Release*): otomatis melepaskan seluruh modifier yang tertahan saat pergantian kendali atau koneksi terputus.
- **Pemeriksa Kesiapan Sistem Ramah Awam (Layman-Friendly System Checker):**
  - Modul mandiri `system_checker.py` dengan checklist visual berwarna (🟢 / 🟡 / 🔴) dan bahasa sehari-hari tanpa istilah teknis membingungkan.
  - Otomatis mendeteksi background service yang sudah aktif di port 8080 (menghindari error crash `Address already in use`), serta menawarkan bantuan otomatis 1-klik untuk perizinan hardware Linux `/dev/uinput` dan Firewall.
- **Mode Game Console (Virtual Gamepad untuk Emulator & Game PC):**
  - Tata letak konsol gamepad virtual penuh di layar sentuh dengan tombol switch cepat `🎮 Game` di toolbar atas.
  - Pilihan kontrol arah ganda: D-Pad 8-arah kinetik dan Analog Thumbstick virtual responsif.
  - Tombol aksi berlian (`A`, `B`, `X`, `Y`), tombol pundak (`L1`, `R1`), dan analog triggers (`L2`, `R2`).
  - Tombol cepat emulator instan: `⏩ Turbo` (Spasi), `💾 Save` (F2), `📂 Load` (F4), dan `⏸️ Menu` (Esc).
  - 4 Preset instan bawaan: RetroArch/SNES, GBA (VisualBoy), PlayStation (PSX/PCSX2), dan Modern WASD/PC.
  - Modal Remap Tombol Mandiri (`⚙️ Remap`) untuk kustomisasi pemetaan tuts keyboard PC per tombol secara bebas dengan penyimpanan permanen di `localStorage`.
- **Sinkronisasi Dua Arah Hardware Caps Lock Host OS:**
  - Deteksi status fisik Caps Lock di host OS secara native di Linux (`/sys/class/leds/*capslock*/brightness` dan X11 ctypes), Windows (`GetKeyState(0x14)`), serta macOS (Quartz AlphaShift).
  - Sinkronisasi status Caps Lock otomatis ke seluruh klien WebSocket yang terhubung via payload `caps_state` dan `pong`.
  - Inversi cerdas huruf besar/kecil (`isUpper = caps_lock !== shift`) pada klien web dan server `uinput`/`pynput`.
- **Mode Presentasi & Meeting Controller (Workstation Remote):**
  - Tata letak kendali slide mandiri dengan tombol sakelar `📽️ Slide` pada toolbar atas.
  - Tombol raksasa ergonomis `NEXT ➡` dan `PREV ⬅` untuk pergantian slide yang nyaman dioperasikan satu tangan di panggung tanpa melihat layar.
  - Tombol layar hitam (`B`), layar putih (`W`), laser pointer (`Ctrl+L`), spidol coret anotasi (`Ctrl+P`), kursor panah (`Ctrl+A`), dan pembersih catatan (`E`).
  - **Digital Countdown Timer Presenter:** Pilihan durasi preset (5m s/d 60m), peringatan visual warna dinamis, dan getaran haptic hening (*silent haptic feedback*) di saku presenter pada menit ke-5, ke-1, dan saat waktu habis.
  - **Mini Laser Trackpad & Air Mouse (Gyro Pointer):** Geser jari untuk mengarahkan pointer di proyektor, atau aktifkan mode Gyro Air untuk mengarahkan laser dengan memiringkan bodi HP secara kinetik (*Device Orientation*).
  - Tombol pintas meeting online (Zoom, Google Meet, Microsoft Teams): Toggle Mute Mikrofon, Kamera Video, Angkat Tangan (*Raise Hand*), dan Bagikan Layar (*Share Screen*).
- **Paket Standalone Executable Lintas Platform:**
  - Skrip build PyInstaller untuk Windows (`build-exe.bat` -> `dist/DigiSmartDeck.exe`), Linux (`build-linux.sh` -> `dist/DigiSmartDeck`), dan macOS (`build-macos.sh` -> `dist/DigiSmartDeckApp.app`).

---

### [1.16.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Persistent Modifier Lock (Paritas Keyboard Fisik PC):**
  - Mengubah mode default modifier menjadi `🔒 Lock`: tombol `Shift`, `Ctrl`, `Alt`, dan `Win`/`Cmd` tetap aktif terus secara visual di layar dan fungsional di host OS hingga ditekan kembali untuk melepaskan.
  - Membuka kapabilitas desktop esensial yang sebelumnya sulit dilakukan di layar sentuh: seleksi teks multi-baris (`Shift + ⬇️ + ⬇️`), navigasi aplikasi berturut-turut (`Alt + Tab + Tab`), pengetikan huruf kapital / simbol bersambung, dan kombinasi shortcut kompleks.
  - Menyediakan 3 mode perilaku modifier yang dapat dipilih pengguna: `🔒 Lock` (aktif terus / persistent), `⚡ 1-Shot` (lepas otomatis setelah 1 karakter), dan `🖐️ Hold` (aktif hanya selama jari menempel pada layar).
  - Tombol sakelar cepat `🔒 Mod` pada toolbar atas tersinkronisasi dua arah secara real-time dengan pilihan di modal Pengaturan.
#### 🛠️ Perbaikan & Stabilitas Backend (Fixed)
- **Server-Side Active Keys State Machine:**
  - Penambahan set pelacak global `ACTIVE_KEYS` di `server.py` untuk mengunci status penekanan tombol secara fisik di kernel Linux `uinput` maupun fallback `pynput`.
  - Memperbaiki `keypress` dan `simulate_tap` agar tidak melepaskan `KEY_LEFTSHIFT` atau modifier lainnya secara prematur saat sedang dalam status aktif/terkunci.

---

### [1.15.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Sistem Pemulihan Mandiri Koneksi Wi-Fi (Self-Healing Network Recovery):**
  - **Zombie Socket Destroyer Watchdog:** Heartbeat ping/pong dengan batas waktu 5.5 detik untuk mendeteksi dan memutus socket TCP zombie seketika saat router Wi-Fi me-reboot tanpa sinyal TCP RST.
  - **Reconnection Loop Cerdas:** Auto-reconnect otomatis dengan exponential backoff dan jitter acak guna mencegah badai koneksi.
  - **Screen-Wake & Network Event Listeners:** Mendengarkan event `online`, `offline`, dan `visibilitychange` (seketika mencoba rekoneksi saat layar HP dinyalakan kembali dari saku atau sleep).
  - **Floating Reconnection Assistant Banner:** Banner bantuan pintar yang muncul otomatis jika rekoneksi gagal >3 kali, dilengkapi tombol coba lagi manual dan pemindai subnet.
  - **Pemindai Subnet Paralel (Dynamic Subnet Scanner):** Scanner paralel (batch 24 IP) pada port 8080 untuk memeriksa endpoint `/api/version` dan mendeteksi IP baru PC secara otomatis jika DHCP router mengubah alamat IP host setelah restart.
  - **Dukungan Resolusi mDNS:** Mengintegrasikan alamat lokal permanen `http://Jarvis.local:8080` dan modal asisten koneksi untuk mengarahkan klien ke IP baru dengan 1 ketukan.
#### 🛠️ Perbaikan & Infrastruktur (Fixed)
- **Pembersihan Konflik Daemon Port 8080:** Mengeliminasi duplikasi daemon antara PM2 dan Systemd yang berebut port 8080.
- **Pembaruan Skrip Rilis:** Memperbarui `bump-version.sh` agar me-restart systemd service `digikeyboard.service` secara bersih saat versi dinaikkan.

---

### [1.14.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Progressive Web App (PWA) & Zero-Popup Fullscreen:**
  - Penambahan Web App Manifest (`manifest.json`) dan Service Worker (`sw.js`) dengan strategi network-first untuk caching aset statis secara instan.
  - Ikon aplikasi HD multi-resolusi (192px, 512px, maskable, dan favicon SVG) untuk opsi *"Add to Home Screen"*.
  - Memberikan pengalaman aplikasi keyboard native layar penuh murni tanpa bilah URL browser dan bebas dari popup peringatan fullscreen browser Chrome.

---

### [1.13.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Opsi Matikan / Sembunyikan Trackpad (Trackpad On/Off Toggle):**
  - Tombol sakelar On/Off trackpad laptop di modal Pengaturan (⚙️), toolbar atas (`🖱️ Pad`), dan sandaran tangan (*palm rest*).
  - Saat dimatikan, dek trackpad tersembunyi sepenuhnya memberikan ruang kanvas maksimal bagi tombol keyboard. Status tersimpan di *localStorage*.

---

### [1.12.1] - 2026-09-26
#### 🛠️ Perbaikan (Fixed)
- **Penyempurnaan Auto-Detect Host OS:** Optimasi deteksi platform browser klien untuk mencocokkan profil OS (Windows / macOS / Ubuntu) dan insets safe area pada layar HP/tablet berponi atau berpulau.

---

### [1.12.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Studio Tipografi & Pemilih Font Mandiri (Custom Typography Studio):**
  - Pemilih font mandiri di modal Pengaturan dengan 10 jenis font: Bawaan Tema (Auto), Ubuntu, Segoe UI, SF Pro, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, dan Sistem UI.
  - Pengguna bebas memadukan font favorit dengan tema visual apa pun.

---

### [1.11.1] - 2026-09-26
#### 🎨 Perubahan (Changed)
- **Pemisahan Menu Target OS & Tema Visual:**
  - Memisahkan pilihan profil Sistem Operasi (Windows, macOS, Ubuntu) dari pilihan tema visual keyboard, memungkinkan pengguna Ubuntu memakai tema Retro 90s, atau pengguna Windows memakai tema Nord Arctic.

---

### [1.11.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Tema Visual Khas Sistem Operasi:**
  - Penambahan tema native: Windows 11 Fluent, macOS Chiclet, dan Ubuntu Yaru Aubergine dengan tipografi dan warna aksen resmi tiap OS.

---

### [1.10.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Dukungan Linux Kernel Virtual Hardware (`uinput`):**
  - Integrasi driver virtual keyboard kernel Linux via `/dev/uinput` (`setup-uinput.sh`).
  - Memungkinkan pengetikan pada Layar Login Display Manager (GDM, SDDM, LightDM), Lock Screen, dan kolom kata sandi root (`sudo`).

---

### [1.9.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Pengontrol Volume Suara Klik Mekanikal:**
  - Slider volume suara klik (10% s/d 100%) dan 3 preset cepat (Pelan, Sedang, Keras) di modal Pengaturan dengan persistensi *localStorage*.

---

### [1.8.1] - 2026-09-26
#### 🛠️ Perbaikan (Fixed)
- **Optimasi Audio Speaker HP & Tombol Uji Suara:**
  - Penalaan osilator Web Audio API (`triangle` 1500Hz→350Hz) agar terdengar renyah pada speaker ponsel pintar kecil, disertai tombol uji suara di Pengaturan.

---

### [1.8.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Mechanical Click Synthesizer:** Umpan balik audio klik sakelar mekanikal sintetik via Web Audio API tanpa beban unduhan berkas audio eksternal.

---

### [1.7.0] - 2026-09-26
#### 🎨 Perubahan (Changed)
- **Integrasi Slider Sensitivitas Trackpad:** Memindahkan pengatur kecepatan kursor mouse ke dalam modal Pengaturan untuk tampilan layar yang lebih rapi.

---

### [1.6.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Pengaturan Efek Getar Haptic Feedback:** Preset intensitas getar motor HP (Lembut 15ms, Normal 30ms, Kuat 50ms) di modal Pengaturan.

---

### [1.5.2] - 2026-09-26
#### 🛠️ Perbaikan (Fixed)
- Perbaikan isolasi CSS fullscreen tip dan tombol tutup tip langsung.

---

### [1.5.1] - 2026-09-26
#### 🛠️ Perbaikan (Fixed)
- Menghilangkan modifier strip atas dan menyembunyikan tip otomatis saat masuk mode fullscreen.

---

### [1.5.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- Penambahan pengaturan ukuran & skala tinggi trackpad (Kecil, Normal, Besar, Ekstra, dan slider 60%-180%).

---

### [1.4.1] - 2026-09-26 (Stable Golden Checkpoint)
#### 🛠️ Perbaikan & Stabilitas (Fixed & Stabilized)
- **Perbaikan Critical Syntax Error Client:** Memperbaiki penutupan blok kurung kurawal `}` pada *event listener* trackpad kanan di `static/index.html` yang sempat menyebabkan *parser crash* pada browser HP/Tablet.
- **Pembersihan Fitur Fullscreen Otomatis:** Membatalkan percobaan *auto-fullscreen* dan mengembalikan kendali manual melalui tombol `⛶` demi stabilitas rendering di semua jenis peramban mobile.
- **Sistem Versi Otomatis Terpusat:** Menetapkan berkas `VERSION` sebagai *single source of truth*, integrasi endpoint `/api/version`, serta penambahan lencana versi di modal Pengaturan.
- **Milestone Stabil:** Menetapkan versi `1.4.1` sebagai titik aman optimal terverifikasi (koneksi instan, 5 tema skin, slider ukuran tombol, continuous key repeat, dan trackpad multi-touch).

---

### [1.4.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Modal Pengaturan Tema & Skin Keyboard:** Tombol pengaturan `⚙️` dengan 5 tema visual kustom: *Dark Modern*, *Retro 90s*, *Cyberpunk*, *Stealth*, dan *Nord Arctic*.
- **Pengatur Ukuran & Skalabilitas Tombol:** Slider granular `30px` hingga `60px` dan 4 preset tinggi tombol.
- **Penyimpanan Preferensi (Persistence):** Semua preferensi tersimpan di *localStorage*.

---

### [1.3.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Continuous Key Auto-Repeat:** Menahan tombol keyboard memicu input berulang otomatis (~22 karakter/detik setelah jeda awal 350ms) seperti keyboard fisik PC.
- **Interactive Trackpad Position Switcher:** Tombol sakelar `⇅ Posisi: Atas / Bawah` untuk memindahkan dek trackpad ke atas atau bawah keyboard.

---

### [1.2.0] - 2026-09-26
#### ✨ Fitur Baru (Added)
- **Laptop Trackpad Deck:** Penambahan modul trackpad terintegrasi dengan palm rest.
- **Multi-Touch Gestures:** 1 Jari gerak kursor, 1 Jari tap klik kiri, 2 Jari tap klik kanan, 2 Jari geser vertikal untuk scroll.
- **Tombol Fisik Klik Kiri & Kanan:** Virtual clickpad dengan dukungan aksi drag-and-drop.

---

### [1.1.0] - 2026-09-26
#### 📚 Dokumentasi & Arsitektur (Added)
- Dokumentasi komprehensif bilingual (`README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/COMMERCIAL_GUIDE.md`, `LICENSE`).
- Smart LAN IP Detection dengan penyaringan interface virtual / VPN.

---

### [1.0.0] - 2026-09-26
#### 🚀 Rilis Awal (Initial Release)
- 1:1 Canvas Physical PC Keyboard tanpa popup keyboard virtual bawaan HP.
- Low-latency Python `aiohttp` WebSocket server dan `pynput` input pipeline.
- Sticky/latch modifier keys, multi-finger touch, panel Fn/Nav/Numpad, dan skrip runner Linux/Windows.

---

## English

### [1.19.0] - 2026-10-05
- Release v1.19.0 updates

### [1.18.6] - 2026-10-05
- Release v1.18.6 updates

### [1.18.5] - 2026-10-05
- Release v1.18.5 updates

### [1.18.4] - 2026-10-05
- Release v1.18.4 updates

### [1.18.3] - 2026-10-05
- Release v1.18.3 updates

### [1.18.2] - 2026-10-05
- Release v1.18.2 updates

### [1.18.1] - 2026-10-05
- Release v1.18.1 updates

### [1.18.0] - 2026-10-05
- Release v1.18.0 updates

### [1.17.0] - 2026-09-28
#### ✨ Added
- **Native Android Client App (`DigiSmartDeck.apk`):**
  - Dedicated Android standalone project located in `android/` utilizing high-performance WebView and modern Android 14 SDK.
  - **True Immersive Sticky Fullscreen:** Eliminates browser Chrome warning toasts (*"Swipe down from the top to exit full screen"*) and installation banners.
  - Features *Auto-Landscape*, *Keep Screen Awake*, and *Soft Keyboard Suppressed* (guaranteeing that native virtual keyboards never cover keycaps).
  - Instant local download link: `http://<PC_IP>:8080/download/apk` with a 1-tap download button inside the Settings modal.
- **Native Bluetooth HID Hardware Emulation (Plug & Play without PC Server):**
  - Integrated `BluetoothHidHelper.java` (Android 9+ API 28) using USB Composite HID Report Descriptor standards (Keyboard + Mouse).
  - Emulates an authentic physical wireless keyboard & mouse directly recognized by Windows, macOS, Linux, iPadOS, Android TV, and UEFI/BIOS menus without requiring server software on the host.
  - Quick `📶 BT` switch button integrated into the web client toolbar.
- **Anti-Collision Single Active Controller Arbitration:**
  - Single active controller arbitration in `server.py`: the first connected device is automatically designated `🟢 👑 Active Controller`.
  - Secondary connected devices enter `🟡 Standby Mode` with server-side keystroke gating to prevent interleaved typing and pointer jitter.
  - Features 1-tap `⚡ Takeover` button, automatic takeover after 30 seconds of primary inactivity, and clean modifier release on handoff/disconnect.
- **Beginner-Friendly Pre-Flight Diagnostics Engine (`system_checker.py`):**
  - Standalone pre-flight checklist module featuring color-coded status (🟢 / 🟡 / 🔴) in plain everyday language.
  - Automatically identifies existing background services on port 8080 (preventing `Address already in use` crashes), offering 1-click remedies for Linux `/dev/uinput` permissions and firewall setup.
- **Game Console Mode (Virtual Gamepad for Emulators & PC Games):**
  - Full-screen virtual gamepad layout with a dedicated `🎮 Game` toggle in the header toolbar.
  - Dual directional control options: 8-way kinetic D-Pad and a responsive virtual analog thumbstick.
  - Diamond action buttons (`A`, `B`, `X`, `Y`), shoulder bumpers (`L1`, `R1`), and analog triggers (`L2`, `R2`).
  - Instant emulator hotkeys: `⏩ Turbo` (Space), `💾 Save` (F2), `📂 Load` (F4), and `⏸️ Menu` (Esc).
  - 4 Built-in instant presets: RetroArch/SNES, GBA (VisualBoy), PlayStation (PSX/PCSX2), and Modern WASD/PC.
  - Dedicated key remapping modal (`⚙️ Remap`) for customizing physical PC key assignments per button with persistent `localStorage` saving.
- **Two-Way Host OS Caps Lock Hardware Synchronization:**
  - Native host OS Caps Lock detection across Linux (`/sys/class/leds/*capslock*/brightness` and X11 ctypes), Windows (`GetKeyState(0x14)`), and macOS (Quartz AlphaShift).
  - Real-time Caps Lock state broadcasting to all connected clients via `caps_state` and `pong` payloads.
  - Smart case inversion (`isUpper = caps_lock !== shift`) on web clients and `uinput`/`pynput` server engines.
- **Presentation & Virtual Meeting Controller Mode:**
  - Standalone presentation slide remote view toggled via the `📽️ Slide` toolbar button.
  - Oversized, ergonomic `NEXT ➡` and `PREV ⬅` thumb controls designed for blind, distraction-free stage navigation.
  - Screen blanking (`B`), white screen (`W`), laser pointer (`Ctrl+L`), pen annotator (`Ctrl+P`), arrow cursor (`Ctrl+A`), and clear drawing notes (`E`).
  - **Presenter Digital Countdown Timer:** Preset duration selector (5m to 60m), dynamic visual color warning, and silent haptic vibration alerts in the speaker's pocket at 5 minutes remaining, 1 minute remaining, and at 0 minutes.
  - **Mini Laser Trackpad & Gyro Air Pointer:** 1-finger touchpad for cursor navigation, plus kinetic device orientation air-mouse mode (tilt smartphone to aim pointer directly on the projector screen).
  - Online meeting quick toggles (Zoom, Google Meet, Microsoft Teams): Mic Mute, Video Camera, Raise Hand, and Screen Share.
- **Multi-Platform Standalone Portable Executables:**
  - Automated PyInstaller compilation scripts for Windows (`build-exe.bat` -> `dist/DigiSmartDeck.exe`), Linux (`build-linux.sh` -> `dist/DigiSmartDeck`), and macOS (`build-macos.sh` -> `dist/DigiSmartDeckApp.app`).

---

### [1.16.0] - 2026-09-26
#### ✨ Added
- **Persistent Modifier Lock (Physical Keyboard Parity):**
  - Set default modifier behavior to `🔒 Lock`: modifier keys (`Shift`, `Ctrl`, `Alt`, and `Win`/`Cmd`) remain actively held down on both the client canvas and the host operating system until tapped again to release.
  - Delivers authentic desktop ergonomics on touchscreens: enables seamless multi-line text selection (`Shift + ⬇️ + ⬇️`), serialized application tab switching (`Alt + Tab + Tab`), continuous uppercase/symbol typing, and complex multi-key combinations without modifier state dropouts.
  - Introduced 3 selectable modifier behaviors: `🔒 Lock` (Persistent active), `⚡ 1-Shot` (Auto-release after 1 subsequent keystroke), and `🖐️ Hold` (Active strictly while finger touches keycap).
  - Real-time two-way synchronization between the header toolbar `🔒 Mod` toggle and the Settings modal selector.
#### 🛠️ Fixed
- **Server-Side Active Keys State Machine:**
  - Added global `ACTIVE_KEYS` set tracking in `server.py` to preserve keydown state across kernel Linux `uinput` and `pynput` controllers.
  - Fixed `keypress` and `simulate_tap` routines to prevent premature release of `KEY_LEFTSHIFT` and other modifiers while held in active lock mode.

---

### [1.15.0] - 2026-09-26
#### ✨ Added
- **Self-Healing Wi-Fi Network Recovery:**
  - **Zombie Socket Destroyer Watchdog:** 5.5s ping/pong heartbeat timeout to immediately detect and terminate stale TCP sockets when the Wi-Fi router reboots without emitting TCP RST/FIN packets.
  - **Smart Reconnection Loop:** Auto-reconnect with exponential backoff and randomized jitter to prevent connection storms.
  - **Screen-Wake & Network Event Handlers:** Proactive reconnect triggers on `visibilitychange` (when unlocking phone or waking screen) and `online`/`offline` browser events.
  - **Floating Reconnection Assistant Banner:** Contextual helper banner appearing automatically after >3 consecutive failures, offering instant retry and subnet scanning options.
  - **Parallel Subnet IP Scanner:** Background parallel scanner (batch size of 24 IPs) on port 8080 querying `/api/version` to locate the PC's newly assigned IP address when DHCP dynamically alters host addressing after a router reboot.
  - **mDNS Hostname Support:** Integration with zero-configuration domain `http://Jarvis.local:8080` and 1-tap redirect modal.
#### 🛠️ Fixed
- **Port 8080 Daemon Cleanup:** Eliminated duplicate daemons between PM2 and Systemd competing for port 8080.
- **Release Automation Script:** Updated `bump-version.sh` to cleanly restart `digikeyboard.service` via systemd.

---

### [1.14.0] - 2026-09-26
#### ✨ Added
- **Progressive Web App (PWA) & Zero-Popup Fullscreen:**
  - Added Web App Manifest (`manifest.json`) and Service Worker (`sw.js`) with network-first offline asset caching.
  - High-resolution multi-size app icons (192px, 512px, maskable, SVG) for "Add to Home Screen".
  - Enables genuine native edge-to-edge fullscreen execution without browser URL bars and completely suppresses intrusive Chrome fullscreen warning banners.

---

### [1.13.0] - 2026-09-26
#### ✨ Added
- **Laptop Trackpad On/Off Toggle:**
  - Full toggle switch in the Settings modal (⚙️), header toolbar (`🖱️ Pad`), and palm rest to turn off the trackpad deck entirely.
  - Hides the trackpad to allocate maximum canvas area for typing, with persistent state stored in `localStorage`.

---

### [1.12.1] - 2026-09-26
#### 🛠️ Fixed
- **Enhanced Host OS & Viewport Detection:** Improved client-side browser platform detection to automatically match OS profiles (Windows, macOS, Ubuntu) and handle safe-area insets on notched/island displays.

---

### [1.12.0] - 2026-09-26
#### ✨ Added
- **Custom Typography Studio:** Independent font selector in the Settings dialog featuring 10 font choices (Theme Default, Ubuntu, Segoe UI, SF Pro, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, System UI).

---

### [1.11.1] - 2026-09-26
#### 🎨 Changed
- **Separated Target OS & Visual Themes:** Decoupled operating system key layouts from visual color palettes, enabling any visual theme (Retro 90s, Nord, Cyberpunk) across Windows, macOS, or Ubuntu layout profiles.

---

### [1.11.0] - 2026-09-26
#### ✨ Added
- **Native Operating System Themes:** Added authentic Windows 11 Fluent, macOS Chiclet, and Ubuntu Yaru Aubergine visual themes.

---

### [1.10.0] - 2026-09-26
#### ✨ Added
- **Linux Kernel Virtual Hardware Driver (`uinput`):**
  - Integrated direct kernel input injection via `/dev/uinput` (`setup-uinput.sh`).
  - Unlocks full keyboard functionality on Display Manager Login Screens (GDM, SDDM, LightDM), Lock Screens, and `sudo` root password prompts.

---

### [1.9.0] - 2026-09-26
#### ✨ Added
- **Mechanical Switch Audio Volume Controller:** Granular volume slider (10% to 100%) and 3 quick presets (Quiet, Medium, Loud) with `localStorage` persistence.

---

### [1.8.1] - 2026-09-26
#### 🛠️ Fixed
- **Mobile Speaker Tuning & Audio Test Button:** Adjusted Web Audio API oscillator curve (`triangle` 1500Hz→350Hz) for clarity on compact mobile speakers and added an instant test audio button in Settings.

---

### [1.8.0] - 2026-09-26
#### ✨ Added
- **Mechanical Click Synthesizer:** Real-time dual-oscillator acoustic switch simulation using Web Audio API without external audio file downloads.

---

### [1.7.0] - 2026-09-26
#### 🎨 Changed
- **Trackpad Sensitivity Relocation:** Moved mouse pointer sensitivity slider inside the Settings modal for a cleaner canvas.

---

### [1.6.0] - 2026-09-26
#### ✨ Added
- **Haptic Vibration Feedback:** Configurable tactile feedback presets (Soft 15ms, Normal 30ms, Strong 50ms) in Settings.

---

### [1.5.2] - 2026-09-26
#### 🛠️ Fixed
- Fixed CSS isolation for fullscreen tips and added instant dismiss button.

---

### [1.5.1] - 2026-09-26
#### 🛠️ Fixed
- Removed top modifier strip and automatically hid tip banner in fullscreen mode.

---

### [1.5.0] - 2026-09-26
#### ✨ Added
- Added trackpad sizing and deck height scale options (Compact, Normal, Large, XL, and 60%-180% slider).

---

### [1.4.1] - 2026-09-26 (Stable Golden Checkpoint)
#### 🛠️ Fixed & Stabilized
- **Client Script Syntax Fix:** Resolved missing closing brace `}` in right trackpad click handler in `static/index.html`.
- **Manual Fullscreen Restored:** Restored standard manual toggle `⛶` for cross-platform stability.
- **Centralized Automated Versioning:** Introduced `VERSION` file as single source of truth, `/api/version` endpoint, and version badge in Settings.

---

### [1.4.0] - 2026-09-26
#### ✨ Added
- **Settings Modal & Themes:** Bespoke visual themes: *Dark Modern*, *Retro 90s*, *Cyberpunk*, *Stealth*, and *Nord Arctic*.
- **Key Sizing:** Granular key height scaling slider from `30px` to `60px`.
- **Full Client Persistence:** All custom preferences saved in `localStorage`.

---

### [1.3.0] - 2026-09-26
#### ✨ Added
- **Continuous Key Auto-Repeat:** Holding down keyboard buttons triggers continuous repeat input (~22 keys/sec after 350ms delay).
- **Interactive Trackpad Position Switcher:** Quick toggle `⇅ Posisi: Atas / Bawah` to swap trackpad deck placement.

---

### [1.2.0] - 2026-09-26
#### ✨ Added
- **Integrated Laptop Trackpad Deck:** Authentic laptop lower deck with centered multi-touch trackpad and physical buttons.
- **Multi-Touch Gestures:** 1-finger move, tap-to-click, 2-finger right click, and 2-finger kinetic vertical scrolling.

---

### [1.1.0] - 2026-09-26
#### 📚 Documentation & Architecture (Added)
- Comprehensive bilingual documentation, architecture specs, roadmap, and commercial guide.
- Smart LAN IP Detection with virtual/VPN interface filtering.

---

### [1.0.0] - 2026-09-26
#### 🚀 Initial Release
- 1:1 Canvas Physical PC Keyboard on mobile browser with zero native mobile keyboard popup.
- Low-latency Python `aiohttp` WebSocket server and `pynput` input pipeline.
- Sticky/latch modifiers, multi-touch support, and quick shortcut panels.
