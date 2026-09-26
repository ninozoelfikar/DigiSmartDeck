# 💼 Commercialization Guide & Business Strategy / Panduan Komersialisasi & Strategi Bisnis

*Read in: [Bahasa Indonesia](#-panduan-komersialisasi-bahasa-indonesia) | [English](#-commercialization-guide-english)*

---

## 🇮🇩 Panduan Komersialisasi (Bahasa Indonesia)

Dokumen ini membedah potensi bisnis, positioning pasar, alternatif branding, model monetisasi, serta strategi peluncuran produk komersial berbasis teknologi DigiKeyboard.

---

### 1. 🏷️ Alternatif Nama Branding Produk

Untuk pasar komersial, nama produk harus mencerminkan nilai fungsional, modern, dan mudah diingat oleh pengguna internasional maupun lokal:

| Nama Brand Alternatif | Nuansa / Vibe | Target Pasar Utama | Nilai Jual / Tagline |
| :--- | :--- | :--- | :--- |
| **AirDeck** *(Sangat Direkomendasikan)* | Ringan, profesional, ala studio | Kreator konten, streamer, presenter | *"Turn Any Phone or Tablet into Your Wireless Studio & Desk Controller"* |
| **DeskPilot** | Produktivitas kerja, kontrol penuh | Pekerja remote, programmer, power user | *"Your Personal Secondary Desktop Cockpit"* |
| **KeyCast** | Cepat, nirkabel, instan | Pengguna umum, media center, presentasi | *"Instant Wireless PC Keyboard & Remote in Your Pocket"* |
| **TapDeck Studio** | Taktil, kreatif, modular | Editor video, desainer, live streamer | *"The Free-form Touch Control Deck for PC Power Users"* |
| **DigiKeyboard Pro** | Langsung, teknis, to-the-point | Pengguna yang butuh keyboard pengganti darurat | *"Full PC Mechanical Keyboard Layout for Mobile Screens"* |

---

### 2. 📊 Analisis Lanskap Pasar & Kompetitor

| Produk | Harga | Kelebihan | Kelemahan / Celah Pasar yang Bisa Anda Rebut |
| :--- | :--- | :--- | :--- |
| **Elgato Stream Deck Mobile** | Langganan ~$2.99/bln atau $49.99 lifetime | Fitur integrasi OBS/Twitch sangat matang | Mahal (model langganan dibenci banyak pengguna); tidak fokus ke keyboard PC standar |
| **Unified Remote** | Freemium ($4.99 full unlock) | Mendukung banyak plugin aplikasi | Tampilan UI terasa usang (era 2014); setup awal membingungkan |
| **Touch Portal** | Freemium ($13.99 Pro) | Fitur macro sangat kaya | Sangat berat; kurva belajar rumit untuk pengguna awam |
| **KDE Connect** | Gratis (Open Source) | Fitur lengkap (clipboard, SMS, remote) | Bukan berorientasi komersial; layout keyboard HP tetap memicu Gboard bawaan HP |
| **Produk Anda (AirDeck / DigiKeyboard)** | **One-time purchase / Freemium** | **Bebas instalasi di HP (Web/PWA), layout fisik 100% PC asli, latensi super rendah, tanpa langganan bulanan** | Produk baru; perlu membangun kredibilitas dan integrasi plugin |

---

### 3. 🎯 3 Jalur Monetisasi Utama

#### Jalur 1: "Macro Pad / Stream Deck Alternative" (Kreator & Streamer) ⭐⭐⭐⭐⭐
* **Permasalahan:** Hardware Elgato Stream Deck berharga Rp 2.000.000 – Rp 4.000.000. Streamer pemula dan pekerja kreatif ingin tombol shortcut fisik tanpa biaya jutaan.
* **Solusi Produk:** Jual template atau lisensi *AirDeck Studio* yang memungkinkan pengguna mengubah tablet lama (iPad atau Android bekas) menjadi control pad interaktif (OBS scene switch, mute mic Discord, audio mixer).
* **Model Pendapatan:** 
  - Lisensi seumur hidup (One-time license key) via **Gumroad** (pasar global) dan **Lynk.id / Mayar** (pasar Indonesia).
  - Paket Icon Pack & Macro Preset tambahan (Rp 25.000 - Rp 50.000).

#### Jalur 2: Freemium Native App (Play Store & App Store) ⭐⭐⭐⭐
* **Strategi:** Bungkus antarmuka web ke dalam aplikasi native (menggunakan Capacitor atau Flutter) agar pengguna dapat mengunduh langsung dari store dengan penemuan server PC otomatis (mDNS zero-config).
* **Tingkat Gratis (Free Tier):**
  - Full PC Keyboard + Touchpad dasar.
* **Tingkat Berbayar (Pro Unlock - In-App Purchase):**
  - Unlimited custom macro buttons.
  - Sound effect switch mekanikal realistis (Cherry MX Blue, Brown, Red).
  - Tema visual eksklusif (Cyberpunk RGB, Retro Macintosh, Nord Minimal).
  - Multi-PC switcher (mengontrol hingga 3 PC berbeda dari satu HP).

#### Jalur 3: Hardware Gadget Bundle (Plug-and-Play USB Dongle) ⭐⭐⭐⭐
* **Konsep:** Buat dongle fisik berbasis mikrokontroler murah (**ESP32-S3** atau **Raspberry Pi Pico W**):
  - Dongle dicolok ke port USB PC. PC langsung mengenalinya sebagai **keyboard USB hardware resmi (HID)** tanpa perlu instal software Python atau konfigurasi server di PC!
  - Dongle memancarkan Wi-Fi Hotspot mini. HP pengguna tersambung ke Wi-Fi dongle dan langsung mengetik.
  - **Kelebihan Revolusioner:** Berfungsi bahkan di BIOS/UEFI, komputer kantor yang terkunci izin instalasi aplikasi, Smart TV, atau PlayStation/Xbox!
* **Biaya Produksi (HPP):** ~Rp 65.000 - Rp 85.000 per unit (Modul ESP32 + 3D printed case).
* **Harga Jual Pasar:** Rp 175.000 - Rp 250.000 di Tokopedia / Shopee.

---

### 4. 💵 Rekomendasi Struktur Penetapan Harga (Pricing)

| Model Penjualan | Wilayah Indonesia (IDR) | Pasar Internasional (USD) |
| :--- | :--- | :--- |
| **Digital License (Lifetime)** | Rp 49.000 – Rp 89.000 (sekali bayar) | $4.99 – $9.99 (one-time payment) |
| **In-App Purchase Pro Unlock** | Rp 39.000 | $3.99 |
| **Physical Hardware Dongle (Plug & Play)** | Rp 189.000 – Rp 249.000 | $19.99 – $24.99 |

---

## 🇬🇧 Commercialization Guide (English)

This document provides a commercial roadmap, competitor landscape analysis, product positioning strategies, branding alternatives, and monetization funnels for commercializing the DigiKeyboard technology.

---

### 1. 🏷️ Branding Alternatives
- **AirDeck**: Professional, creator-focused name for a mobile-to-desktop control deck.
- **DeskPilot**: Geared towards workstation control, multitasking, and productivity.
- **KeyCast**: Fast, frictionless wireless PC keyboard utility.
- **TapDeck Studio**: Premium creator brand for video editors and livestreamers.

### 2. 💡 Value Proposition & Market Differentiators
1. **Zero Client Installation:** Runs instantly in any mobile browser or as a PWA without downloading bloatware from app stores.
2. **True Physical PC Layout:** Avoids invoking irritating native mobile keyboards (Gboard/iOS touch keyboard) by rendering full-fidelity mechanical PC keys directly on the canvas.
3. **No Subscription Trap:** Positioned against expensive SaaS subscription models (like Stream Deck Mobile's monthly fee) as an ethical one-time purchase.

### 3. 🚀 Go-to-Market Execution Plan
1. **Beta Launch (Open Source / Community):** Gain GitHub stars, collect user feedback on Reddit (`r/selfhosted`, `r/pcmasterrace`, `r/mechanicalkeyboards`), and refine stability.
2. **PWA & Touchpad Update:** Complete the core product functionality with seamless mobile installation and virtual mouse gestures.
3. **Monetize Macro & Theming Features:** Launch the Pro version with custom macro designer and digital store presence on Gumroad.
