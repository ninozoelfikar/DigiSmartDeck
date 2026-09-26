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

### 📌 Fase 1: PWA, Estetika Mekanikal & Optimasi Tablet (Q1 2026)
- [ ] **PWA (Progressive Web App):**
  - Web App Manifest & Service Worker untuk opsi *"Add to Home Screen"*.
  - Menghilangkan address bar & navigasi browser 100% (true edge-to-edge native look).
- [ ] **Aesthetic Themes (Mechanical Keycap Studio):**
  - **Retro IBM 1990s Beige:** Warna klasik abu-abu/krem komputer legendaris.
  - **Cyberpunk Neon RGB:** Efek cahaya backlit RGB responsif saat tombol ditekan.
  - **Stealth Matte Black:** Nuansa minimalis hitam matte elegan.
  - **GMK Botanical / Pastel:** Tema estetika minimalis modern.
- [ ] **Synthesized Switch Sound Effect (Audio Taktil):**
  - Pilihan efek suara klik sakelar mekanikal (Cherry MX Blue Clicky, Brown Tactile, Red Linear, Thoccy).
- [ ] **Optimasi Tablet 10–12 Inci (Full 100% Layout):**
  - Rasio jarak tombol proporsional untuk pengetikan 10 jari di iPad / Android Tablet.
- [ ] **Split Ergonomic Mode (Khusus HP):**
  - Membelah keyboard menjadi dua sisi (kiri & kanan) agar jempol tangan kiri dan kanan dapat mengetik santai tanpa menjangkau area tengah layar yang jauh.

---

### 📌 Fase 2: Virtual Trackpad & Developer Toolset (Q2 2026)
- [ ] **Side Mini-Trackpad Companion:**
  - Area trackpad mini di sisi kanan atau atas keyboard tanpa perlu berganti tab halaman.
- [ ] **Gesture Multi-Touch Penuh:**
  - 1 Jari: Menggerakkan kursor mouse PC secara kinetik.
  - 1 Tap: Klik kiri | 2 Tap: Klik kanan.
  - 2 Jari Geser: Scroll dokumen & web (vertikal / horizontal).
  - Pinch-to-zoom: Zoom in / zoom out dokumen.
- [ ] **Developer & Sysadmin Power Bar:**
  - Tombol 1-tap khusus karakter terminal yang sering hilang di HP: `|` (pipe), `~` (tilde), `\`, `sudo `, `git `, `$`, `{ }`, `->`.
  - Mode Vim/Nano lock (Esc, Ctrl+C, Ctrl+Z, Tab, Arrow keys selalu siaga).
- [ ] **Panel Media PC:** Slider pengatur master volume, mute mic/speaker, dan playback controller.

---

### 📌 Fase 3: Keamanan & Pairing Cerdas (Q3 2026)
- [ ] **4-Digit Pairing PIN:**
  - Layar PC memunculkan 4 angka acak yang wajib dimasukkan pada HP sebelum koneksi diizinkan. Ini mencegah serangan iseng/injeksi tombol pada Wi-Fi publik (kafe/kampus/kantor).
- [ ] **Device Whitelist & Session Tokens:**
  - Menyimpan token HP yang telah terverifikasi agar koneksi berikutnya otomatis terhubung tanpa perlu memasukkan PIN berulang.
- [ ] **mDNS / Zero-Config Local Domain:**
  - Akses langsung via `http://digikeyboard.local:8080` tanpa perlu mengingat deretan angka IP.

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
- [ ] **PWA & Edge-to-Edge Experience:** Zero-browser address bar when launched from the home screen.
- [ ] **Mechanical Keycap Theme Engine:** Retro 1990s Beige, Cyberpunk Neon RGB, and Stealth Matte Dark.
- [ ] **Acoustic Switch Feedback:** Optional synthesized mechanical switch click sounds (Clicky Blue, Tactile Brown, Thoccy Linear).
- [ ] **Dedicated Tablet 10–12" Layout:** Optimized key pitch for 10-finger typing on iPads and Android tablets.
- [ ] **Ergonomic Split Thumb Mode:** Split-half layout for handheld smartphone typing.

### 📌 Phase 2: Integrated Touchpad & Sysadmin Toolset
- [ ] **Side Mini-Trackpad:** Compact trackpad area alongside the keyboard for simultaneous pointer & typing control.
- [ ] **Multi-Touch Gestures:** Kinetic mouse movement, tap-to-click, and smooth dual-axis scrolling.
- [ ] **Terminal & Sysadmin Bar:** One-tap keys for `|`, `~`, `\`, `sudo`, `git`, `$`, `Esc`, and `Ctrl+C`.
- [ ] **Media & Master Volume Controller:** Slider for audio control and playback buttons.

### 📌 Phase 3: Pairing Security & Local Networking
- [ ] **One-Time Pairing PIN:** 4-digit terminal code required to authenticate mobile clients on shared Wi-Fi networks.
- [ ] **Trusted Device Sessions:** Cryptographic tokens to auto-reconnect trusted mobile devices.
- [ ] **Zero-Config mDNS:** Broadcast URL as `http://digikeyboard.local:8080`.

### 📌 Phase 4: Creator Macro Pad & Production Packaging
- [ ] **Interactive Macro Grid:** Custom 3x4 / 4x4 tile layout for streaming (OBS), podcasting, and editing suites.
- [ ] **Desktop System Tray Wrapper:** Lightweight taskbar executable with auto-launch capabilities.
- [ ] **Standalone Hardware Dongle (ESP32-S3):** Plug-and-play USB hardware HID firmware.
