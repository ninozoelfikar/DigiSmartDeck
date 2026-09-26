# 🗺️ Product Roadmap & Visual Innovation / Rencana Pengembangan & Inovasi Visual

*Read in: [Bahasa Indonesia](#-roadmap-produk-bahasa-indonesia) | [English](#-product-roadmap-english)*

---

## 🇮🇩 Roadmap Produk (Bahasa Indonesia)

Roadmap ini memetakan tahapan rilis fitur untuk mentransformasi DigiKeyboard dari utilitas keyboard sederhana menjadi **wireless workstation controller** kelas profesional, dengan fokus mempertahankan keunggulan visual utamanya: **Zero Native Mobile Keyboard Popup & True 1:1 Physical PC Canvas**.

```mermaid
gantt
    title Roadmap Pengembangan DigiKeyboard
    dateFormat  YYYY-Q1
    section Phase 1 (Visual, UX & PWA)
    PWA & Zero-Browser Frame     :p1, 2026-Q1, 30d
    Mechanical Themes & Audio   :p2, after p1, 20d
    Tablet 10-12" Full-Size Mode:p2b, after p1, 15d
    section Phase 2 (Input & Companion)
    Side Mini-Trackpad & Gestures:p3, after p2, 30d
    Developer/Sysadmin Toolset   :p3b, after p3, 15d
    Media & Volume Knobs        :p4, after p3b, 15d
    section Phase 3 (Security & Conn)
    4-Digit PIN Pairing Modal   :p5, after p4, 20d
    Encrypted Local Frames      :p6, after p5, 15d
    section Phase 4 (Pro & Business)
    Custom Macro / Stream Deck  :p7, after p6, 40d
    Desktop Tray App (Tauri)    :p8, after p7, 30d
```

---

### 🎨 Celah Pasar Visual (Visual White Space & USP)
Sebagian besar aplikasi remote PC (seperti *Unified Remote* atau *WiFi Mouse*) memunculkan kotak input teks yang memicu **keyboard bawaan HP (Gboard/iOS)** menutupi separuh layar, menghilangkan tombol penting PC (`Esc`, `Tab`, `Ctrl`, `Alt`, `F1-F12`, `|`, `~`).

**DigiKeyboard** mengambil pendekatan berbeda: **menggambar layout keyboard mekanik PC 1:1 langsung di kanvas layar**, bebas dari gangguan keyboard virtual bawaan HP.

---

### 📌 Fase 1: Estetika Mekanikal, Audio Taktil & Optimasi Tampilan (Selesai di v1.9.0)
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

### 📌 Fase 2: Virtual Trackpad & Developer Toolset (Sebagian Selesai di v1.9.0)
- [x] **Laptop Trackpad Companion:**
  - Area trackpad laptop virtual di sisi **Atas** atau **Bawah** keyboard tanpa perlu berganti tab.
  - Pengaturan ukuran trackpad fleksibel (Kecil, Normal, Besar, Ekstra, dan slider 60%-180%).
  - Pengatur sensitivitas gerak kursor (0.5x s/d 3.0x).
  - **Opsi Matikan/Sembunyikan Trackpad (On/Off Toggle):** Dukungan penonaktifan dek trackpad secara penuh dari menu pengaturan, toolbar atas, dan tombol palm rest dengan penyimpanan status permanen.
- [x] **Gesture Multi-Touch Penuh:**
  - 1 Jari: Menggerakkan kursor mouse PC secara kinetik (throttled ~120fps).
  - 1-Finger Tap: Klik kiri | 2-Finger Tap: Klik kanan.
  - 2 Jari Geser: Scroll vertikal dokumen & web.
  - Tombol Fisik: Tombol klik kiri & kanan laptop deck dengan status visual responsif.
- [ ] **Developer & Sysadmin Power Bar:**
  - Tombol 1-tap khusus karakter terminal yang sering hilang di HP: `|` (pipe), `~` (tilde), `\`, `sudo `, `git `, `$`, `{ }`, `->`.
  - Mode Vim/Nano lock (Esc, Ctrl+C, Ctrl+Z, Tab, Arrow keys selalu siaga).
- [ ] **Panel Media PC:** Slider pengatur master volume PC, mute mic/speaker, dan playback controller.

---

### 📌 Fase 3: Keamanan & Pemulihan Koneksi Cerdas (Sebagian Selesai di v1.15.0)
- [x] **Sistem Pemulihan Mandiri Koneksi Wi-Fi (Self-Healing Network Recovery):**
  - Pemutus socket zombie otomatis (heartbeat ping/pong dengan watchdog 5.5s timeout) saat router Wi-Fi me-reboot tanpa sinyal TCP RST.
  - Reconnection loop dengan exponential backoff dan jitter acak.
  - Event listener `online`, `offline`, dan `visibilitychange` (bangun dari layar mati / latar belakang).
  - Floating Reconnection Assistant banner saat gagal terhubung >3 kali.
  - Pindai Subnet Otomatis (`scanSubnet`) paralel pada port 8080 untuk mendeteksi IP baru PC jika DHCP router mengalihkan IP setelah reboot, didukung resolusi mDNS (`Jarvis.local`).
  - Modal pengalihan IP/hostname manual.
- [ ] **4-Digit Pairing PIN:**
  - Layar PC memunculkan 4 angka acak yang wajib dimasukkan pada HP sebelum koneksi diizinkan. Ini mencegah serangan iseng/injeksi tombol pada Wi-Fi publik (kafe/kampus/kantor).
- [ ] **Device Whitelist & Session Tokens:**
  - Menyimpan token HP yang telah terverifikasi agar koneksi berikutnya otomatis terhubung tanpa perlu memasukkan PIN berulang.
- [x] **Persistent Modifier Lock (Paritas Keyboard Fisik PC):**
  - Penguncian aktif terus tombol modifier (`Shift`, `Ctrl`, `Alt`, `Win`/`Cmd`) untuk seleksi teks multi-baris (`Shift + ⬇️ + ⬇️`) dan navigasi tab bersambung (`Alt + Tab + Tab`).
  - Mendukung 3 mode: `🔒 Lock` (persisten), `⚡ 1-Shot` (lepas otomatis), dan `🖐️ Hold` (tahan manual).
- [x] **mDNS / Zero-Config Local Domain:**
  - Dukungan resolusi domain mDNS (`Jarvis.local:8080`) dan fallback scanner otomatis.

---

### 📌 Fase 4: Studio Macro Deck & Distribusi Komersial (Q4 2026)
- [ ] **Custom Macro Deck Grid:**
  - Grid 3x4 atau 4x4 tombol khusus kreator (OBS Studio Scene Switch, Discord Mute, Adobe Premiere hotkeys).
- [ ] **Desktop System Tray Wrapper:**
  - Aplikasi mini di taskbar Windows/Linux/macOS dengan ikon tray untuk *Start on Boot*, *Show QR*, dan *Settings*.
- [ ] **Packaging Hardware Dongle (ESP32-S3):**
  - Firmware mikrokontroler USB Plug-and-Play yang langsung dikenali sebagai keyboard USB hardware tanpa instal software di PC.

---

## 🇬🇧 Product Roadmap (English)

### 🎨 Visual Differentiation (USP)
Unlike conventional remote apps (e.g., Unified Remote) which invoke awkward native mobile keyboards (Gboard/iOS) that swallow half the display, DigiKeyboard renders a **full-fidelity 1:1 mechanical PC keyboard canvas**, keeping all essential PC keys (`Esc`, `Tab`, `F1-F12`, `Ctrl`, `Alt`, `|`, `~`) immediately reachable.

### 📌 Phase 1: Progressive Web App & Mechanical Aesthetics
- [x] **PWA & Edge-to-Edge Experience:** Zero-browser address bar and zero Chrome fullscreen popups when launched from the home screen via Web App Manifest & Service Worker.
- [x] **Mechanical Keycap Theme Engine:** Native OS, Retro 1990s Beige, Cyberpunk Neon RGB, Stealth Matte Dark, and Nord Arctic.
- [x] **Acoustic Switch Feedback:** Synthesized mechanical switch click sounds via Web Audio API with granular volume controls and test audio button.
- [x] **Custom Font Studio:** Independent typography selector with 10 font choices.
- [ ] **Dedicated Tablet 10–12" Layout:** Optimized key pitch for 10-finger typing on iPads and Android tablets.
- [ ] **Ergonomic Split Thumb Mode:** Split-half layout for handheld smartphone typing.

### 📌 Phase 2: Integrated Touchpad & Sysadmin Toolset
- [x] **Integrated Trackpad Companion:** Multi-touch laptop trackpad deck with kinetic pointer tracking, tap-to-click, 2-finger scroll, physical buttons, sensitivity/size scaling, and full On/Off toggle.
- [ ] **Terminal & Sysadmin Bar:** One-tap keys for `|`, `~`, `\`, `sudo`, `git`, `$`, `Esc`, and `Ctrl+C`.
- [ ] **Media & Master Volume Controller:** Slider for audio control and playback buttons.

### 📌 Phase 3: Pairing Security & Local Networking
- [x] **Self-Healing Wi-Fi Reconnection:** 5.5s ping/pong watchdog to terminate zombie sockets, jittered exponential backoff auto-reconnect, screen-wake listeners, and parallel subnet port 8080 scanner to recover dynamically changed PC IP addresses upon router reboot.
- [ ] **One-Time Pairing PIN:** 4-digit terminal code required to authenticate mobile clients on shared Wi-Fi networks.
- [ ] **Trusted Device Sessions:** Cryptographic tokens to auto-reconnect trusted mobile devices.
- [x] **Persistent Modifier Lock (Physical Keyboard Parity):** Continuous active lock for `Shift`, `Ctrl`, `Alt`, and `Win`/`Cmd` enabling seamless multi-line selection (`Shift + ⬇️ + ⬇️`) and serialized desktop shortcuts (`Alt + Tab + Tab`) with 3 selectable behaviors (`🔒 Lock`, `⚡ 1-Shot`, `🖐️ Hold`).
- [x] **Zero-Config mDNS:** Support for hostname broadcast and resolution via `.local:8080`.

### 📌 Phase 4: Creator Macro Pad & Production Packaging
- [ ] **Interactive Macro Grid:** Custom 3x4 / 4x4 tile layout for streaming (OBS), podcasting, and editing suites.
- [ ] **Desktop System Tray Wrapper:** Lightweight taskbar executable with auto-launch capabilities.
- [ ] **Standalone Hardware Dongle (ESP32-S3):** Plug-and-play USB hardware HID firmware.
