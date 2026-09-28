# 🚀 Dokumen Rencana Pemasaran Strategis: DigiKeyboard (AirDeck)

---

## 📌 Ringkasan Eksekutif (Executive Summary)

**DigiKeyboard** (dengan nama komersial yang direkomendasikan: **AirDeck**) adalah solusi software utilitas yang mengubah smartphone atau tablet menjadi keyboard fisik PC standar lengkap dan multitouch trackpad nirkabel via Wi-Fi lokal berlatensi ultra-rendah (1–5 ms), tanpa memicu keyboard virtual bawaan HP (Gboard/SwiftKey).

Rencana pemasaran ini dirancang untuk mengeksekusi strategi penetrasi pasar dengan pendekatan **Product-Led Growth (PLG)** dan **Bootstrapping**, memanfaatkan kekuatan open-source untuk membangun basis pengguna setia (*early adopters*), kemudian mengonversinya menjadi pendapatan melalui produk *Pro/Commercial License* berbiaya terjangkau.

---

## 🎯 1. Positioning & Proposisi Nilai (Unique Value Proposition)

### Pernyataan Positioning
> *"Bagi pengguna PC, teknisi, dan kreator konten yang membutuhkan kendali nirkabel instan atau keyboard cadangan darurat, **DigiKeyboard** adalah solusi remote controller PC tercepat dan paling presisi di browser tanpa instalasi aplikasi HP, berbeda dengan aplikasi remote lain yang memunculkan keyboard HP bawaan yang menutupi layar."*

### Pilar Nilai Utama:
1. **Zero Client Friction (Tanpa Install di HP):** Berjalan langsung di browser modern / PWA via QR scan.
2. **True Physical PC Layout:** Tuts fungsional lengkap (Esc, Tab, Ctrl/Alt/Win/Cmd, F1–F12, Numpad) dengan tactile haptic & sound.
3. **Ultra-Low Latency:** WebSocket lokal 1–5 ms, responsif untuk mengetik cepat dan navigasi kursor.
4. **Linux-Grade Deep Integration:** Mampu menembus lock screen dan sudo terminal via driver `uinput`.

---

## 🔍 2. Analisis Situasi Pasar (SWOT Analysis)

| **Strengths (Kekuatan)** | **Weaknesses (Kelemahan)** |
| :--- | :--- |
| • Zero-install di sisi smartphone (PWA/Web-based).<br>• Tidak memunculkan Gboard/keyboard HP yang mengganggu.<br>• Fitur lengkap: Trackpad multitouch, F1-F12, Numpad, tema visual.<br>• Sangat ringan dan latensi sangat rendah (WebSocket lokal). | • Masih membutuhkan runtime Python di PC host (sebelum ada .exe mandiri).<br>• Terbatas pada satu jaringan Wi-Fi lokal (belum mendukung WAN/Cloud relay).<br>• Brand awareness baru dan belum memiliki verifikasi publisher di OS. |
| **Opportunities (Peluang)** | **Threats (Ancaman)** |
| • Tingginya pengguna HP/tablet bekas yang menganggur di rumah.<br>• Komunitas pecinta mechanical keyboard & desk setup yang sangat visual.<br>• Frustrasi massal pengguna terhadap model langganan bulanan software utilitas.<br>• Potensi ekspansi ke hardware murah plug-and-play (ESP32 dongle). | • Solusi gratis bawaan ekosistem (KDE Connect, Windows Phone Link).<br>• Firewall Windows/Antivirus yang memblokir port lokal 8080 bagi pengguna awam.<br>• Aplikasi kompetitor lama di Google Play Store dengan SEO kuat. |

---

## 🧩 3. Bauran Pemasaran (Marketing Mix - 4P)

### A. Product (Produk)
* **Tier Community (FOSS):** Host script Python open source gratis di GitHub untuk membangun kredibilitas dan *developer trust*.
* **Tier Pro Standalone:** Aplikasi Windows executable (`.exe` 1-klik tanpa Python), Wake-on-LAN, custom macro grid (ala Virtual Stream Deck), dan proteksi PIN/Pairing.
* **Tier Hardware (Fase Lanjutan):** Modul USB dongle ESP32 plug-and-play siap pakai.

### B. Price (Harga)
* **Free Tier (Personal & Game Mode):** **Rp 0** (Keyboard PC, Trackpad, Gamepad & Steering Wheel Gyro gratis selamanya; monetisasi via donasi sukarela/Saweria/Trakteer).
* **Pro All-Access License (Sekali Bayar / Lifetime):**
  - **Harga Resmi Penuh (Full Price):** **Rp 250.000** (Pasar Global: **$15.99 USD**).
  - **Promo Peluncuran (Early-Bird Launch):** **Rp 99.000** (Pasar Global: **$6.99 USD**) untuk 250 pembeli pertama.
* **Mikrotransaksi Skin & Tema Premium (Collector Theme):**
  - **Rp 10.000 / item** (Pasar Global: **$0.99 USD / item**).
  - Pembelian impulsif 1-klik via QRIS untuk skin visual eksklusif (misal: *Gundam Mecha, Retro Macintosh 1984, Vaporwave Sunset, RGB Reactive Chroma, & Custom Switch Audio Packs*).
* **Monetisasi Slot Stiker Palm Rest (Free Tier Ads & Affiliate):**
  - **Model Afiliasi:** Link diskon periferal tech, gaming gear, atau cloud/hosting di e-commerce (Tokopedia/Shopee/Amazon) dengan komisi 5% - 12% per penjualan.
  - **Sewa Slot Sponsor Brand:** Brand teknologi / gaming gear menyewa slot banner stiker tetap (misal: Rp 1.500.000 – Rp 3.000.000 / slot / bulan).
  - *Perk Pro:* Pengguna Pro All-Access bebas dari semua stiker sponsor (Clean Minimalist Deck) atau dapat menempelkan stiker kustom sendiri.
* **B2B / Lab License (Institusi / Kampus):** **Rp 999.000 / instansi** ($99.00 USD).

### C. Place (Distribusi Penjualan)
* **Distribusi Software:**
  - Kode & Versi Komunitas: **GitHub Releases**.
  - Versi Pro (Global): **Gumroad** / **Lemon Squeezy** (menerima Kartu Kredit, Apple Pay, PayPal).
  - Versi Pro (Indonesia): **Mayar** / **Lynk.id** / **Trakteer** (pembayaran QRIS, GoPay, OVO, Virtual Account).
* **PWA Deployment:** Hosted static web frontend di cloud/CDN untuk fallback.

### D. Promotion (Promosi & Akuisisi)
* Mengutamakan kanal organik, konten video pendek demonstratif, dan komunitas teknis (akan dibedah di Bagian 4).

---

## 📣 4. Arsitektur Funnel Pemasaran & Kanal Promosi

```
   ┌────────────────────────────────────────────────────────┐
   │       TOFU: Awareness (Jangkauan Luas / Masif)         │
   │  • TikTok, Reels, Shorts (Video "Penyelamat Laptop")   │
   │  • Reddit (r/homelab, r/mechanicalkeyboards)          │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │    MOFU: Consideration (Edukasi & Pembuktian Solusi)   │
   │  • GitHub Repository & Demo GIF interaktif             │
   │  • Artikel tutorial di Medium, DEV.to, Kaskus/Forum    │
   │  • Review micro-influencer tech / setup desk           │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │     BOFU: Conversion (Pembelian Lisensi Pro)           │
   │  • Landing page dengan perbandingan Free vs Pro        │
   │  • Checkout cepat 1-klik dengan QRIS / Apple Pay       │
   │  • Penawaran Launch Discount (Early Bird)              │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │      Retention & Referral (Advokasi Pengguna)          │
   │  • Program afiliasi kreator (komisi 30%)               │
   │  • Komunitas Discord untuk request fitur / macro pack  │
   └────────────────────────────────────────────────────────┘
```

### 1. Kanal TOFU (Top of Funnel - Kesadaran Merek)
* **Short-Form Video (TikTok, Instagram Reels, YouTube Shorts):**
  - **Hook 1 (Problem-Solver):** *"Keyboard laptop lu rusak pas ngerjain tugas malem-malem? Jangan panik, pake trik HP ini!"*
  - **Hook 2 (Aesthetic/Nerd):** *"Ubah tablet nganggur jadi mechanical keyboard wireless futuristik lengkap sama suaranya!"*
  - **Hook 3 (Living Room Hack):** *"Nonton film di TV dari kasur tapi males bawa mouse keyboard gede? Cukup buka browser HP!"*
* **Komunitas Teknis Global:**
  - **Reddit:** Thread demonstrasi di `r/selfhosted`, `r/homelab`, `r/raspberry_pi`, `r/linux`, `r/badUIbattles` (irony marketing).
  - **Hacker News (Show HN):** *"Show HN: DigiKeyboard – Full physical PC keyboard layout on mobile screen without triggering Gboard"*.

### 2. Kanal MOFU (Middle of Funnel - Pertimbangan)
* **SEO & Content Marketing:**
  - Artikel blog teknis: *"Cara mengontrol PC dari HP tanpa instal aplikasi"*, *"How to control headless Linux server during Wi-Fi setup"*, *"Best DIY Stream Deck alternatives for iPad"*.
* **Dokumentasi & GitHub README:**
  - Menyediakan visual GIF demo tajam (durasi 5 detik) di bagian atas README yang menunjukkan klik trackpad dan pengetikan tanpa delay.

### 3. Kanal BOFU (Bottom of Funnel - Konversi Penjualan)
* **Landing Page Konversi Tinggi:**
  - Landing page minimalis berisi video interaktif, daftar fitur pembeda Pro, dan tombol CTA tunggal: **"Beli Lisensi Seumur Hidup - Rp 49.000"**.
* **Jaminan Bebas Risiko:**
  - 14 hari uang kembali tanpa syarat jika aplikasi tidak berfungsi di jaringan pengguna.

---

## 🗓️ 5. Jadwal Peluncuran Go-To-Market (GTM Timeline)

```
M-2 (Persiapan)     M-1 (Beta & Teaser)       M-0 (Hari Peluncuran)     M+1 s/d M+3 (Skalasi)
───────┬─────────────────────┬──────────────────────────┬─────────────────────────►
       │                     │                          │
       ▼                     ▼                          ▼
• Build .exe 1-klik    • Distribusi ke 20         • Show HN & Reddit Blast   • Ads berbayar (retargeting)
• Siapkan Landing      beta tester                • Peluncuran Product Hunt  • Kerjasama 10 micro-kreator
  Page & Toko Digital  • Teaser video TikTok/     • Diskon Early-Bird 40%    • Rilis ekstensi Macro Pack
• Dokumentasi GIF        Reels (organic testing)  • Email blast ke subscriber
```

* **Fase 1: Pra-Peluncuran (Minggu -2 s/d Minggu -1):**
  - Membuat binary `.exe` Windows mandiri via PyInstaller agar non-programmer bisa langsung mencoba.
  - Setup gateway pembayaran di Mayar/Lynk.id (ID) dan Lemon Squeezy/Gumroad (Global).
  - Menyiapkan aset kreatif: rekaman video demo horizontal & vertikal 4K, mockup tablet.
* **Fase 2: Hari Peluncuran (Minggu 0):**
  - Peluncuran serentak di **Product Hunt** (fokus meraih Top 5 Product of the Day).
  - Posting Show HN di Hacker News dan thread demonstrasi di subreddit r/selfhosted.
  - Membuka diskon peluncuran 40% (Rp 29.000 / $2.99) untuk 500 pembeli pertama.
* **Fase 3: Pasca-Peluncuran & Skalasi (Bulan 1 s/d 3):**
  - Merekrut 10 micro-influencer tech di TikTok/Instagram untuk membuat video ulasan organik (sistem barter lisensi Pro + komisi afiliasi 30%).
  - Memperkenalkan paket preset macro (OBS Studio Pack, Photoshop Pack).

---

## 📊 6. Metrik Keberhasilan & KPI Utama

| Tahap Funnel | Indikator Kinerja Utama (KPI) | Target 3 Bulan Pertama |
| :--- | :--- | :--- |
| **Awareness** | • Total tayangan video (Shorts/TikTok/Reels)<br>• GitHub Stars | • > 500.000 views<br>• > 1.500 GitHub Stars |
| **Acquisition** | • Unique visitors ke landing page<br>• Download/Clone versi Community | • 25.000 pengunjung unik<br>• 5.000 instalasi aktif |
| **Monetization** | • Konversi Visitor ke Pembeli Lisensi Pro<br>• Total Unit Terjual (Pro License)<br>• Total Pendapatan Bersih | • Rasio konversi 2.5% – 3.5%<br>• 750 – 1.000 lisensi terjual<br>• **Rp 35.000.000 – Rp 50.000.000** |
| **Customer Satisfaction** | • Tingkat pengembalian dana (Refund Rate) | • < 2% |

---

## 💰 7. Estimasi Anggaran Pemasaran (Bootstrapping Budget)

Pendekatan ini berfokus pada efisiensi modal maksimal (*lean startup*):

| Komponen Pengeluaran | Alokasi Dana (IDR) | Keterangan |
| :--- | :--- | :--- |
| **Domain & Hosting Landing Page** | Rp 250.000 | Domain `.app` / `.dev` (1 tahun), hosting di Vercel/Cloudflare (Gratis). |
| **Payment Gateway Setup & Transaction Fees** | Pay-as-you-go (~3-5%) | Tanpa biaya di muka (dipotong saat terjadi penjualan). |
| **Kerjasama Micro-Creator & Afiliasi** | Rp 1.500.000 | Biaya stimulus / *seed capital* untuk 3-5 kreator video TikTok/Reels. |
| **Paid Amplification (Ads Uji Coba)** | Rp 1.000.000 | Uji coba TikTok/Meta Ads pada video pemenang (winning content). |
| **Total Anggaran Awal** | **Rp 2.750.000** | Sangat terjangkau untuk validasi pasar awal. |

---

## ✅ Tindakan Prioritas Segera (Immediate Action Items)

1. [ ] **Kemas Binary Standalone:** Buat file `.exe` Windows (single-file executable) agar pengguna non-teknis bisa langsung menjalankan tanpa instalasi Python.
2. [ ] **Buat 3 Konsep Video Pendek:** Rekam video 15 detik demonstrasi layar HP mengetik di PC dengan audio klik mekanikal yang jernih.
3. [ ] **Siapkan Toko Digital:** Buka akun penjual di Mayar/Lynk.id (untuk pasar lokal) dan Lemon Squeezy (untuk pasar global).
4. [ ] **Perbarui Banner README:** Tambahkan badge visual dan tautan demo langsung untuk memaksimalkan konversi pengunjung GitHub.
