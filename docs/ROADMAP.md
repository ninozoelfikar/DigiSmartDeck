# 🗺️ Product Roadmap / Rencana Pengembangan Fitur

*Read in: [Bahasa Indonesia](#-roadmap-produk-bahasa-indonesia) | [English](#-product-roadmap-english)*

---

## 🇮🇩 Roadmap Produk (Bahasa Indonesia)

Roadmap ini memetakan tahapan rilis fitur untuk mentransformasi DigiKeyboard dari utilitas keyboard sederhana menjadi workstation controller nirkabel kelas profesional.

```mermaid
gantt
    title Roadmap Pengembangan DigiKeyboard
    dateFormat  YYYY-Q1
    section Phase 1 (Core & UX)
    PWA & Home Screen App       :p1, 2026-Q1, 30d
    Custom Haptics & Themes     :p2, after p1, 20d
    section Phase 2 (Input Expansion)
    Virtual Touchpad & Gestures :p3, after p2, 30d
    Media & Volume Knobs        :p4, after p3, 15d
    section Phase 3 (Security)
    4-Digit PIN Pairing Modal   :p5, after p4, 20d
    Encrypted Local Frames      :p6, after p5, 15d
    section Phase 4 (Pro & Business)
    Custom Macro / Stream Deck  :p7, after p6, 40d
    Desktop Tray App (Tauri)    :p8, after p7, 30d
```

### 📌 Fase 1: PWA (Progressive Web App) & UI Polish (Q1 2026)
- [ ] **Manifest & Service Worker:** Memungkinkan pengguna menekan *"Add to Home Screen"* di Chrome/Safari HP.
- [ ] **Zero-Browser Frame:** Saat diluncurkan dari icon layar utama, browser toolbar dan address bar hilang 100%, menghasilkan sensasi aplikasi native.
- [ ] **Tema Tampilan:** Mode Dark Mechanical, Retro 90s Grey, Cyberpunk RGB, dan Paper Minimalist.
- [ ] **Suara Sakelar Mekanikal Opsional:** Audio feedback klik switch (Blue/Brown/Red switch sound effects).

### 📌 Fase 2: Virtual Trackpad & Mouse Expansion (Q2 2026)
- [ ] **Tab Trackpad Terintegrasi:** Berpindah antara mode Keyboard dan Touchpad hanya dengan satu geseran.
- [ ] **Gesture Multi-Touch:**
  - 1 Jari: Menggerakkan kursor mouse.
  - 1 Tap: Klik kiri.
  - 2 Tap: Klik kanan.
  - 2 Jari Geser Vertikal/Horizontal: Scroll halaman web dan dokumen.
  - Pinch-to-zoom: Zoom in / zoom out dokumen.
- [ ] **Panel Media PC:** Slider pengatur volume master PC, tombol mute, dan kontrol playback video.

### 📌 Fase 3: Keamanan & Pemasangan Terproteksi (Q3 2026)
- [ ] **PIN Pairing 4-Digit:** Layar terminal PC memunculkan 4 angka acak yang wajib dimasukkan pada HP sebelum koneksi diizinkan. Ini mencegah perangkat asing di kafe/kantor mengendalikan PC Anda.
- [ ] **Daftar Perangkat Terpercaya (Device Whitelist):** Menyimpan token browser HP yang telah terverifikasi agar tidak perlu memasukkan PIN berulang kali.
- [ ] **mDNS / Local Hostname:** Akses melalui `http://digikeyboard.local:8080` tanpa perlu mengetik IP manual.

### 📌 Fase 4: Studio Macro Deck & Distribusi Komersial (Q4 2026)
- [ ] **Custom Macro Deck Grid:** Grid 3x4 atau 4x4 tombol khusus kreator (OBS Studio Scene Switch, Discord Mute, Adobe Premiere hotkeys).
- [ ] **Desktop System Tray Wrapper:** Aplikasi mini di taskbar Windows/Linux/macOS dengan ikon tray untuk *Start on Boot*, *Show QR*, dan *Settings*.

---

## 🇬🇧 Product Roadmap (English)

### 📌 Phase 1: Progressive Web App (PWA) & Aesthetics
- [ ] **PWA Manifest & Offline Caching:** Allow instant installation to mobile home screens.
- [ ] **Standalone Immersive Mode:** Run edge-to-edge without browser URL bars or navigation elements.
- [ ] **Theme Studio:** Dark mechanical, retro aesthetic, and RGB reactive backlights.
- [ ] **Mechanical Audio Feedback:** Optional synthesis of mechanical clicky/linear key sounds.

### 📌 Phase 2: Integrated Virtual Trackpad & Multimedia
- [ ] **Touchpad Surface:** Smooth cursor acceleration, dual-axis kinetic scrolling, and tap-to-click.
- [ ] **Multi-Finger Gestures:** Two-finger right-click, three-finger window cycling (`Alt+Tab`).
- [ ] **Media Deck:** Smooth master volume slider, mute toggles, and media track playback controllers.

### 📌 Phase 3: Pairing Security & Local Discovery
- [ ] **One-Time Pairing PIN:** Prevent unauthorized keystroke injection on shared public Wi-Fi networks.
- [ ] **Persistent Device Tokens:** Auto-reconnect authenticated devices via cryptographic session tokens.
- [ ] **mDNS Zero-Config:** Broadcast local service discovery as `digikeyboard.local`.

### 📌 Phase 4: Creator Macro Pad & Standalone Desktop Apps
- [ ] **Programmable Macro Grid:** Configurable action tiles with custom icons for streaming (OBS), podcasting, and editing suites.
- [ ] **Desktop Native Tray Executable:** Bundled via lightweight runtime (Tauri or PySystray) with auto-start on boot.
