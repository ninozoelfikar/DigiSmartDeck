# 🗺️ Product Roadmap & Visual Innovation / Rencana Pengembangan & Inovasi Visual

*Read in: [Bahasa Indonesia](#-roadmap-produk-bahasa-indonesia) | [English](#-product-roadmap-english)*

---

## 🇮🇩 Roadmap Produk (Bahasa Indonesia)

Roadmap ini memetakan tahapan rilis fitur untuk mentransformasi DigiKeyboard dari utilitas keyboard sederhana menjadi **wireless multi-mode workstation & entertainment controller** kelas profesional, dengan fokus mempertahankan keunggulan visual utamanya: **Zero Native Mobile Keyboard Popup & True 1:1 Physical PC Canvas**.

```mermaid
gantt
    title Roadmap Pengembangan DigiKeyboard
    dateFormat  YYYY-Q1
    section Phase 1 (Visual, UX & PWA)
    PWA & Zero-Browser Frame        :done, p1, 2026-Q1, 30d
    Mechanical Themes & Audio      :done, p2, after p1, 20d
    Custom Font Typography Studio  :done, p2b, after p2, 15d
    section Phase 2 (Trackpad & Input)
    Laptop Trackpad Companion      :done, p3, after p2b, 30d
    Persistent Modifier Lock       :done, p3b, after p3, 15d
    section Phase 3 (Network & Security)
    Self-Healing Wi-Fi Watchdog    :done, p4, after p3b, 20d
    4-Digit PIN Pairing Security   :p5, after p4, 20d
    section Phase 4 (Multi-Mode Controllers)
    Mode Presentasi & Zoom Meeting :p6, after p5, 30d
    Custom AI Pad & Media Remote   :p7, after p6, 25d
    Mode Canvas / Freehand Drawing :p8, after p7, 25d
    Mode Gamepad & Wheel Steer     :p9, after p8, 35d
    Mode Live Stream & Soundboard  :p10, after p9, 30d
    Mode Potret (Portrait Layout)  :p11, after p10, 15d
    section Phase 5 (Commercial & Hardware)
    Build .exe & License Validator :p12, after p11, 20d
    System Tray Wrapper & Dongle   :p13, after p12, 30d
```

---

### 🎨 Celah Pasar Visual (Visual White Space & USP)
Sebagian besar aplikasi remote PC (seperti *Unified Remote* atau *WiFi Mouse*) memunculkan kotak input teks yang memicu **keyboard bawaan HP (Gboard/iOS)** menutupi separuh layar, menghilangkan tombol penting PC (`Esc`, `Tab`, `Ctrl`, `Alt`, `F1-F12`, `|`, `~`).

**DigiKeyboard** mengambil pendekatan berbeda: **menggambar kanvas interaktif fungsional langsung di layar ponsel/tablet**, bebas dari gangguan keyboard virtual bawaan HP.

---

### 📌 Fase 1: Estetika Mekanikal, Audio Taktil & Optimasi Tampilan (Selesai di v1.9.0 - v1.14.0)
- [x] **Pemilih Sistem Operasi Terpisah (Target OS Architecture):**
  - **Windows:** Layout tombol `Ctrl` • `⊞ Win` • `Alt`, font Segoe UI, pintasan `Win+D`, `Alt+Tab`, `Ctrl+Alt+Del`.
  - **macOS:** Layout tombol Apple `control ⌃` • `option ⌥` • `⌘ cmd`, font SF Pro, pintasan Mac `⌘+C`, `⌘+Tab`, `⌘+Space`, `⌥+⌘+Esc`.
  - **Ubuntu / Linux:** Layout tombol `Ctrl` • `❖ Super` • `Alt`, font Ubuntu, pintasan `Super+D`, `Ctrl+Alt+T`.
- [x] **Aesthetic Keycap Theme Studio:**
  - **Sesuai OS (Native):** Otomatis menggunakan warna & estetika visual khas OS yang dipilih (Windows 11 Fluent, macOS Chiclet, Ubuntu Yaru Aubergine).
  - **Dark Modern:** Tampilan gelap netral GitHub style.
  - **Retro IBM 1990s Beige:** Warna klasik komputer legendaris dengan font Courier New.
  - **Cyberpunk Neon RGB:** Aksen cyan & magenta tajam dengan font futuristik Orbitron.
  - **Stealth Matte Black:** Nuansa minimalis monokromatik dengan font JetBrains Mono.
  - **Nord Frost:** Palet biru beku Skandinavia dengan font Inter.
- [x] **Studio Tipografi & Pemilih Font Mandiri (Custom Key Fonts):** Pilihan 10 jenis font (Bawaan Tema/Auto, Ubuntu, Segoe UI, SF Pro, JetBrains Mono, Inter, Fira Code, Orbitron, Courier New, Sistem UI) yang dapat dipilih bebas terpisah dari tema aktif.
- [x] **Synthesized Switch Sound Effect (Audio Taktil) & Pengontrol Volume:**
  - Sintetis suara saklar mekanikal renyah via Web Audio API tanpa file eksternal.
  - Pengontrol volume granular (10% s/d 100%) dan 3 preset volume instan (Pelan, Sedang, Keras).
  - Tombol uji audio langsung di modal pengaturan.
- [x] **Haptic Feedback Controller:**
  - Pilihan preset getaran: Lembut (15ms), Normal (30ms), Kuat (50ms).
- [x] **Edge-to-Edge & Fullscreen Experience:**
  - Tombol manual fullscreen (`⛶`) di toolbar atas dan opsi sembunyikan baris tip.
- [x] **PWA (Progressive Web App):**
  - Web App Manifest (`manifest.json`), Service Worker (`sw.js`), dan ikon HD multi-resolusi (192px, 512px, maskable, SVG) untuk opsi *"Add to Home Screen"*. Menjalankan aplikasi secara native fullscreen murni tanpa address bar dan bebas popup peringatan Chrome.
- [ ] **Split Ergonomic Mode (Khusus HP):**
  - Membelah keyboard menjadi dua sisi (kiri & kanan) agar jempol tangan kiri dan kanan dapat mengetik santai tanpa menjangkau area tengah layar yang jauh.

---

### 📌 Fase 2: Virtual Trackpad & Input Pipeline (Selesai di v1.10.0 - v1.16.0)
- [x] **Laptop Trackpad Companion:**
  - Area trackpad laptop virtual di sisi **Atas** atau **Bawah** keyboard tanpa perlu berganti tab.
  - Pengaturan ukuran trackpad fleksibel (Kecil, Normal, Besar, Ekstra, dan slider 60%-180%).
  - Pengatur sensitivitas gerak kursor (0.5x s/d 3.0x).
  - **Opsi Matikan/Sembunyikan Trackpad (On/Off Toggle):** Dukungan penonaktifan dek trackpad secara penuh dari menu pengaturan, toolbar atas, dan tombol palm rest dengan penyimpanan status permanen.
- [x] **Gesture Multi-Touch Penuh:**
  - 1 Jari: Menggerakkan kursor mouse PC secara kinetik (throttled ~120fps).
  - 1-Finger Tap: Klik kiri | 2-Finger Tap: Klik kanan.
  - 2 Jari Geser: Scroll vertikal dokumen & web.
  - Tombol Fisik: Tombol klik kiri & kanan laptop deck dengan status visual responsif dan aksi drag-and-drop.
- [x] **Dukungan Linux Kernel Virtual Hardware (`uinput`):**
  - Injeksi hardware langsung level kernel via `/dev/uinput` untuk pengetikan pada Layar Login GDM/SDDM, Lock Screen, dan prompt sudo password.
- [x] **Continuous Key Auto-Repeat:** Menahan tombol keyboard menghasilkan input berulang otomatis (~22 karakter/detik setelah jeda awal 350ms) seperti keyboard fisik PC.
- [x] **Persistent Modifier Lock (Paritas Keyboard Fisik PC):**
  - Penguncian aktif terus tombol modifier (`Shift`, `Ctrl`, `Alt`, `Win`/`Cmd`) untuk seleksi teks multi-baris (`Shift + ⬇️ + ⬇️`), navigasi tab bersambung (`Alt + Tab + Tab`), dan pengetikan huruf kapital berkelanjutan.
  - Menyediakan 3 mode: `🔒 Lock` (persisten), `⚡ 1-Shot` (lepas otomatis), dan `🖐️ Hold` (tahan manual).
- [ ] **Developer & Sysadmin Power Bar:**
  - Tombol 1-tap khusus karakter terminal yang sering hilang di HP: `|` (pipe), `~` (tilde), `\`, `sudo `, `git `, `$`, `{ }`, `->`.
  - Mode Vim/Nano lock (Esc, Ctrl+C, Ctrl+Z, Tab, Arrow keys selalu siaga).
- [ ] **Slot Banner Stiker Sponsor Palm Rest (Estetika Stiker Laptop):**
  - Desain area kiri & kanan trackpad bergaya stiker laptop khas anak muda/kreator (native & non-intrusive).
  - Khusus tampil di Free Tier: berfungsi sebagai slot afiliasi periferal/gadget, sewa sponsor brand teknologi, atau promosi internal (Skin Rp 10k & Lisensi Pro).
  - Lisensi Pro otomatis menghilangkan stiker sponsor (Clean Minimalist Deck) atau membuka fitur upload stiker kustom pribadi.

---

### 📌 Fase 3: Keamanan & Pemulihan Jaringan Cerdas (Selesai di v1.15.0)
- [x] **Sistem Pemulihan Mandiri Koneksi Wi-Fi (Self-Healing Network Recovery):**
  - Pemutus socket zombie otomatis (heartbeat ping/pong dengan watchdog 5.5s timeout) saat router Wi-Fi me-reboot tanpa sinyal TCP RST.
  - Reconnection loop dengan exponential backoff dan jitter acak.
  - Event listener `online`, `offline`, dan `visibilitychange` (bangun dari layar mati / latar belakang).
  - Floating Reconnection Assistant banner saat gagal terhubung >3 kali.
  - Pindai Subnet Otomatis (`scanSubnet`) paralel pada port 8080 untuk mendeteksi IP baru PC jika DHCP router mengalihkan IP setelah reboot.
  - Dukungan resolusi domain mDNS permanen (`http://Jarvis.local:8080`) dan modal pengalihan IP manual.
- [ ] **4-Digit Pairing PIN:**
  - Layar PC memunculkan 4 angka acak yang wajib dimasukkan pada HP sebelum koneksi diizinkan untuk mencegah injeksi tombol pada Wi-Fi publik (kafe/kampus/kantor).
- [ ] **Device Whitelist & Session Tokens:**
  - Menyimpan token HP yang telah terverifikasi agar koneksi berikutnya otomatis terhubung tanpa perlu memasukkan PIN berulang.

---

### 📌 Fase 4: Multi-Mode Workstation & Entertainment Controllers (Program Pengembangan Selanjutnya)

Rencana penambahan ragam mode kerja dan kontroler interaktif terdedikasi tanpa memunculkan keyboard bawaan ponsel:

#### 1. 💼 Mode Produktivitas & Kolaborasi
- [ ] **Mode Presentasi (Presentation Remote):**
  - Navigasi slide 1-tap berukuran besar (`Next ➡`, `Prev ⬅`, `First ⏪`, `Last ⏩`).
  - Pointer laser virtual interaktif (memanfaatkan gyroscope/air-mouse HP untuk menggerakkan kursor laser di layar presentasi PC).
  - Tombol layar hitam/kosong (`B` / Blank Screen) dan penyorot pointer (highlighter).
  - Timer waktu presentasi (countdown timer) dan getaran haptic pengingat sisa waktu di HP presenter.
- [ ] **Mode Zoom & Virtual Meeting Streaming:**
  - Panel kontrol rapat 1-tap yang disinkronkan dengan shortcut Zoom, Google Meet, dan Microsoft Teams:
    - Tombol Toggle Mute / Unmute Mikrofon dengan status indikator visual warna (Merah/Hijau).
    - Tombol Toggle Kamera On / Off.
    - Tombol Angkat Tangan (*Raise Hand*).
    - Tombol Bagikan Layar (*Share Screen*).
    - Quick Reaction Emoji Bar (👍, 👏, ❤️, 🎉).
- [ ] **Mode Potret (Portrait Layout):**
  - Tata letak khusus orientasi vertikal/tegak yang dioptimalkan untuk pengoperasian satu tangan saat smartphone dipegang vertikal, atau saat ditaruh pada stand tablet tegak.
  - Penyesuaian proporsi kanvas keyboard dan trackpad atas/bawah yang ergonomis dalam rasio layar potret.

#### 2. 🎨 Mode Kreator, Media & AI Workflow
- [ ] **Custom Mode (Minimalist / AI Workstation Pad):**
  - Tata letak kanvas minimalis yang dapat dikonfigurasi bebas sesuai kebutuhan spesifik alur kerja pengguna.
  - Contoh preset AI Workstation: hanya menampilkan tombol **`Enter` besar**, **Panah Navigasi `▲ ▼ ◀ ▶`**, dan **`Numpad Kalkulator`** untuk mempermudah eksekusi prompt AI, review spreadsheet, atau navigasi terminal dengan satu tangan tanpa kepadatan tombol QWERTY.
- [ ] **Mode Media Controller (Pemutar Hiburan PC):**
  - Remote multimedia mandiri untuk mengontrol Spotify, YouTube, VLC, Netflix, dan pemutar musik PC.
  - Tombol Play / Pause besar, Trek Berikutnya / Sebelumnya, dan tombol lewati 10 detik.
  - Master Volume Dial / Slider virtual interaktif untuk mengatur level volume sistem PC secara halus disertai tombol Mute instan.
- [ ] **Mode Canvas / Freehand / Drawing Tablet:**
  - Kanvas sentuh bebas resolusi tinggi untuk menggambar (*freehand drawing*), membuat sketsa, tanda tangan dokumen digital, dan anotasi whiteboard.
  - Kompatibel dengan input jari maupun digital stylus pen (Apple Pencil, Samsung S-Pen) dengan transmisi koordinat presisi ke aplikasi grafis PC (Photoshop, Figma, Krita, OneNote).
- [ ] **Mode Live Stream & Studio Deck (OBS Studio & Soundboard):**
  - **OBS Studio Controller:** Integrasi WebSocket OBS untuk perpindahan Scene siaran, pergantian Kamera aktif (*Select Cam*), toggle sumber audio, dan tombol Mulai/Hentikan Streaming & Rekaman.
  - **Soundboard Audio FX:** Tombol instan efek suara reaksi siaran langsung (Tepuk Tangan / *Applause*, Tawa / *Laugh*, *Drum Roll*, *Air Horn*, *Ding*) yang langsung diputar ke output audio PC.

#### 3. 🎮 Mode Gaming & Simulasi
- [x] **Mode Game Console (Virtual Gamepad):**
  - Tata letak konsol gamepad virtual penuh di layar sentuh:
    - D-Pad 8-arah di sisi kiri.
    - Tombol aksi `A`, `B`, `X`, `Y` di sisi kanan.
    - Tombol bahu `L1` / `R1` dan trigger analog `L2` / `R2`.
    - Tombol `Start`, `Select`, dan virtual thumbstick analog untuk emulator game retro dan game kasual PC.
- [ ] **Mode Game Wheel Steer (Setir Balap Mobil Virtual):**
  - Mengubah smartphone menjadi setir mobil balap interaktif (*Motion Racing Wheel*) dengan memanfaatkan sensor Gyroscope & Accelerometer perangkat (memutar fisik ponsel ke kiri/kanan untuk membelokkan setir mobil di game balap PC seperti Need for Speed, Forza, atau Assetto Corsa).
  - Dilengkapi kontrol sentuh pedal Gas dan Rem analog di layar, paddle shift untuk perpindahan transmisi manual, dan tombol rem tangan (*Handbrake*).

---

### 📌 Fase 5: Kesiapan Komersial, Distribusi & Hardware (Selesai Sebagian di v1.16.0 - v1.17.0)
- [x] **Script Build Executable Mandiri Multi-Platform (PyInstaller):**
  - **Linux Standalone Binary (`build-linux.sh`):** Menghasilkan executable ELF 64-bit mandiri `dist/DigiKeyboard` (39MB) tanpa dependensi Python di target PC.
  - **Windows Executable (`build-exe.bat`):** Script kompilasi menghasilkan `dist/DigiKeyboard.exe` mandiri beserta aset ikon `.ico`.
  - **macOS Bundle (`build-macos.sh`):** Menghasilkan bundle aplikasi `dist/DigiKeyboardApp.app` dan binary CLI macOS.
- [x] **Aplikasi Android Native & Bluetooth HID (`DigiKeyboard.apk`):**
  - Pengemasan APK Android native via Gradle 8.5 & Android SDK 34 (`build-apk.sh`).
  - True Immersive Sticky Fullscreen bebas gangguan popup Chrome.
  - Emulasi perangkat keras Bluetooth HID komposit (Keyboard + Mouse) via `BluetoothHidDevice` (Android 9+) untuk koneksi langsung tanpa software server.
- [x] **Anti-Collision Single Active Controller Arbitration:**
  - Manajemen sesi multi-koneksi dengan 1 pengendali aktif, antrean siaga (*standby*), dan pengambilalihan (*takeover*).
- [x] **Pemeriksa Pra-Jalan Interaktif (`system_checker.py`):**
  - Diagnostik kesehatan port, firewall, dan izin kernel ramah orang awam.
- [ ] **Mesin Validasi Kunci Lisensi Offline (Cryptographic License Key Validator):**
  - Sistem validasi lisensi Pro berbasis kriptografi asimetris (Ed25519 / HMAC-SHA256) untuk verifikasi offline tanpa ketergantungan koneksi internet/server aktivasi terpusat.
  - Mendukung tipe lisensi (Personal Lifetime, Creator Studio, B2B Multi-seat) dan batas kedaluwarsa opsional.
  - Modal antarmuka aktivasi kunci lisensi (*License Activation Dialog*) di menu Pengaturan (⚙️) dengan status verifikasi visual instan.
- [ ] **Desktop System Tray Wrapper:**
  - Aplikasi mini di taskbar Windows/Linux/macOS dengan ikon tray untuk *Start on Boot*, *Show QR*, dan *Settings*.
- [ ] **Packaging Hardware Dongle (ESP32-S3):**
  - Firmware mikrokontroler USB Plug-and-Play yang langsung dikenali sebagai keyboard USB hardware tanpa instal software di PC.

---

## 🇬🇧 Product Roadmap (English)

### 🎨 Visual Differentiation (USP)
Unlike conventional remote apps (e.g., Unified Remote) which invoke awkward native mobile keyboards (Gboard/iOS) that swallow half the display, DigiKeyboard renders a **full-fidelity interactive canvas**, keeping all essential controls immediately reachable without software keyboard interference.

### 📌 Phase 1: Progressive Web App & Mechanical Aesthetics (Completed)
- [x] **PWA & Edge-to-Edge Experience:** Zero-browser address bar and zero Chrome fullscreen popups when launched from the home screen via Web App Manifest & Service Worker.
- [x] **Mechanical Keycap Theme Engine:** Native OS, Retro 1990s Beige, Cyberpunk Neon RGB, Stealth Matte Dark, and Nord Arctic.
- [x] **Acoustic Switch Feedback:** Synthesized mechanical switch click sounds via Web Audio API with granular volume controls and test audio button.
- [x] **Custom Font Studio:** Independent typography selector with 10 font choices.
- [ ] **Dedicated Tablet 10–12" Layout:** Optimized key pitch for 10-finger typing on iPads and Android tablets.
- [ ] **Ergonomic Split Thumb Mode:** Split-half layout for handheld smartphone typing.

### 📌 Phase 2: Integrated Touchpad & Input Pipeline (Completed)
- [x] **Integrated Trackpad Companion:** Multi-touch laptop trackpad deck with kinetic pointer tracking, tap-to-click, 2-finger scroll, physical buttons, sensitivity/size scaling, and full On/Off toggle.
- [x] **Linux Kernel Virtual Hardware Driver (`uinput`):** Native hardware-level injection for GDM/SDDM display login, lock screen, and root password prompts.
- [x] **Continuous Key Auto-Repeat:** Hardware-like repeat (~22 keys/sec after 350ms delay).
- [ ] **Terminal & Sysadmin Bar:** One-tap keys for `|`, `~`, `\`, `sudo`, `git`, `$`, `Esc`, and `Ctrl+C`.
- [ ] **Palm Rest Laptop Sticker Ad Slots:**
  - Aesthetic digital laptop sticker slots on the left & right margins of the trackpad, mimicking youthful laptop sticker culture.
  - Exclusively on Free Tier: serves tech peripheral affiliate banners, brand sponsorship space, or internal promotions (Skins & Pro).
  - Pro Tier removes all sponsor stickers for a pristine deck or enables user custom stickers.

### 📌 Phase 3: Pairing Security & Local Networking (Completed)
- [x] **Self-Healing Wi-Fi Reconnection:** 5.5s ping/pong watchdog to terminate zombie sockets, jittered exponential backoff auto-reconnect, screen-wake listeners, and parallel subnet port 8080 scanner to recover dynamically changed PC IP addresses upon router reboot.
- [x] **Zero-Config mDNS:** Support for hostname broadcast and resolution via `http://Jarvis.local:8080`.
- [ ] **One-Time Pairing PIN:** 4-digit terminal code required to authenticate mobile clients on shared Wi-Fi networks.
- [ ] **Trusted Device Sessions:** Cryptographic tokens to auto-reconnect trusted mobile devices.

### 📌 Phase 4: Multi-Mode Workstation & Entertainment Controllers (Future Roadmap)

Upcoming dedicated functional controllers designed for specialized workflows:

#### 1. 💼 Productivity & Collaboration
- [ ] **Presentation Mode (Slide Remote):**
  - Oversized 1-tap navigation keys (`Next ➡`, `Prev ⬅`, `First ⏪`, `Last ⏩`).
  - Virtual gyro-assisted laser pointer (air mouse).
  - Blank/black screen button (`B`) and highlighter toggle.
  - Presenter countdown timer with haptic reminder intervals.
- [ ] **Zoom & Virtual Meeting Controller:**
  - One-tap status toggles for Zoom, Google Meet, and Microsoft Teams:
    - Mic Mute / Unmute toggle with red/green visual state indicators.
    - Camera On / Off toggle.
    - Raise Hand & Screen Share controls.
    - Quick meeting reaction emojis (👍, 👏, ❤️, 🎉).
- [ ] **Portrait Mode (Vertical Orientation Layout):**
  - Ergonomically arranged vertical layout tailored for one-handed smartphone use or vertical tablet stands.

#### 2. 🎨 Creators, Media & AI Workflows
- [ ] **Custom Mode (Minimalist / AI Workstation Pad):**
  - Configurable modular keypad tailored for specialized setups (e.g., displaying solely an oversized **`Enter` key**, **Navigation Arrows `▲ ▼ ◀ ▶`**, and a **`Numeric Keypad`** for comfortable single-handed AI prompt engineering, code review, or data entry).
- [ ] **Media Controller Mode:**
  - Dedicated multimedia deck for Spotify, YouTube, VLC, and Netflix.
  - Large Play/Pause, track skip, 10s scrub buttons, and a master volume knob/slider with instant mute.
- [ ] **Canvas / Freehand / Drawing Tablet Mode:**
  - High-precision drawing canvas for freehand sketches, digital signatures, and whiteboard collaboration.
  - Stylus pen support (Apple Pencil, Samsung S-Pen) with accurate coordinates streaming to PC art software (Photoshop, Figma, Krita).
- [ ] **Live Stream & Studio Deck (OBS Studio & Soundboard):**
  - **OBS Studio Controller:** WebSocket integration for switching scenes, camera feeds, audio sources, and stream/recording toggles.
  - **Soundboard FX Pad:** Instant trigger buttons for live broadcast audio reactions (applause, laugh, drum roll, air horn).

#### 3. 🎮 Gaming & Simulation
- [x] **Game Console Mode (Virtual Gamepad):**
  - 8-way directional D-pad, `A-B-X-Y` face buttons, `L1/R1` shoulder buttons, `L2/R2` analog triggers, Start/Select, and virtual thumbstick.
- [ ] **Steering Wheel Mode (Motion Racing Wheel):**
  - Gyroscope & accelerometer-driven steering wheel control (tilt phone to steer cars in racing games like Forza, Assetto Corsa, or NFS).
  - Virtual analog gas and brake pedals, paddle shifters, and handbrake button.

### 📌 Phase 5: Commercial Readiness, Packaging & Hardware (Completed Partially in v1.16.0 - v1.17.0)
- [x] **Multi-Platform Standalone Executable Build Scripts (PyInstaller):**
  - **Linux Standalone ELF Binary (`build-linux.sh`):** Compiles single-file 64-bit binary `dist/DigiKeyboard` (39MB) with zero Python dependencies needed on target machines.
  - **Windows Executable (`build-exe.bat`):** Automated build script producing standalone `dist/DigiKeyboard.exe` with bundled icons and static assets.
  - **macOS Bundle (`build-macos.sh`):** Automated build script for `dist/DigiKeyboardApp.app`.
- [x] **Android Native Client & Bluetooth HID (`DigiKeyboard.apk`):**
  - Native APK packaged using Gradle 8.5 & Android SDK 34 (`build-apk.sh`).
  - True Immersive Sticky Fullscreen eliminating Chrome fullscreen warning toasts and browser address bars.
  - Bluetooth HID composite device emulation (Keyboard + Mouse) via `BluetoothHidDevice` (Android 9+) for direct pairing without server software.
- [x] **Anti-Collision Single Active Controller Arbitration:**
  - Prevents multi-user input conflicts with single active controller, standby queue, 1-tap takeover, and clean modifier release on handoff/disconnect.
- [x] **System Pre-Flight Diagnostics Engine (`system_checker.py`):**
  - Beginner-friendly preflight checks for port 8080 conflicts, uinput permissions, and firewall rules without stack trace crashes.
- [ ] **Cryptographic Offline License Key Validator:**
  - Asymmetric cryptographic license verification engine (Ed25519 / HMAC-SHA256) enabling 100% offline verification without central DRM or internet connectivity requirements.
  - Supports license tiers (Personal Lifetime, Creator Studio, B2B Multi-seat) and optional expiry validations.
  - In-app License Key Activation Dialog in Settings (⚙️) with immediate visual validation feedback.
- [ ] **Desktop System Tray Wrapper:** Lightweight taskbar executable with auto-launch capabilities.
- [ ] **Standalone Hardware Dongle (ESP32-S3):** Plug-and-play USB hardware HID firmware.
