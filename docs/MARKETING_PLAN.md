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

### A. Product (Produk & Ekosistem Plugin)
* **Tier Community (FOSS):** Host script Python open source gratis di GitHub untuk membangun kredibilitas dan *developer trust*.
* **Tier Pro Standalone:** Aplikasi Windows executable (`.exe` 1-klik tanpa Python), Wake-on-LAN, custom macro grid (ala Virtual Stream Deck), dan proteksi PIN/Pairing.
* **Ekosistem Arsitektur Plugin (Modular Capability System):**
  Aplikasi dirancang mendukung sistem ekstensi plugin modular agar pengguna dapat memperluas fungsi sesuai alur kerja spesifik tanpa membebani performa inti:
  - **Plugin Gratis (Free Plugins - Built-in untuk Semua Pengguna):**
    1. *Basic AutoText / Text Snippet:* Template frasa pendek untuk teks harian (salam pembuka, tanda tangan email, kalimat template singkat).
    2. *Kalkulator Numpad Cepat:* Melakukan kalkulasi langsung di HP dan mengirimkan hasil angka ke kursor PC dengan 1 ketukan.
    3. *Media & Slide Remote:* Kontrol volume, pemutar musik/video, dan kendali presentasi dasar.
    4. *AI Action Bar Dasar:* Tombol tuts cepat perintah AI (Ctrl+C, Space, Backspace, Enter ekstra besar).
  - **Plugin Pro (Pro Exclusive Plugins - Driver Konversi Monetisasi Utama):**
    1. *Voice Typing / Wireless Dictation (Speech-to-Text):* Memanfaatkan mikrofon smartphone via Web Speech API / model AI speech lokal untuk mentranskripsikan suara pengguna langsung menjadi ketikan teks real-time di PC host (Word, Google Docs, VS Code, chat) tanpa kabel dan tanpa latensi. Mikrofon HP yang dekat ke mulut menghasilkan akurasi dikte jauh lebih superior dibanding mikrofon bawaan laptop/PC.
    2. *Advanced AutoText & Snippet Engine (Dynamic Macro Expander):* Template teks multi-baris tanpa batas, variabel dinamis (tanggal otomatis, timestamp, clipboard paste), dan trigger prefix instan (misal ketik `;rek` langsung mengetik nama bank & nomor rekening lengkap di PC).
    3. *AI Prompt Dispatcher & Assistant:* Preset generator prompt terstruktur ke ChatGPT/Claude/Gemini/Ollama dengan variabel konteks kustom dalam 1 klik.
    4. *Multi-Action Chaining Macro:* Satu ketukan memicu sekuens kombinasi tuts berurutan dengan jeda presisi (delay milidetik), sangat krusial untuk gamer dan pekerja data entry.
    5. *Cloud / Multi-Device Sync Profile:* Sinkronisasi instan snippet AutoText dan layout kustom antar ponsel, tablet, dan PC host.
* **Tier Hardware (Ekspansi Fisik King Ali Studio):**
  - **Dongle USB ESP32-S3:** Modul USB dongle plug-and-play siap pakai tanpa software PC.
  - **DigiBoard OLED Workstation Deck by King Ali Studio:** Hardware fisik keyboard mekanikal kustom berlayar mini OLED dinamis di tiap tuts/macro key. Tuts fisik bersinkronisasi dua arah secara real-time dengan mode DigiKeyboard (AI mode, Gamepad, Presentasi, Video Scrubbing), sekaligus menjadi etalase fisik tema dan plugin dari DigiKeyboard Store.

### B. Price (Harga)
* **Free Tier (Personal & Game Mode):** **Rp 0** (Keyboard PC, Trackpad, Gamepad & Steering Wheel Gyro gratis selamanya; monetisasi via donasi sukarela/Saweria/Trakteer).
* **Pro All-Access License (Sekali Bayar / Lifetime):**
  - **Harga Resmi Penuh (Full Price):** **Rp 250.000** (Pasar Global: **$15.99 USD**).
  - **Promo Peluncuran (Early-Bird Launch):** **Rp 99.000** (Pasar Global: **$6.99 USD**) untuk 250 pembeli pertama.
* **Mikrotransaksi Skin & Tema Premium (Collector Theme):**
  - **Rp 10.000 / item** (Pasar Global: **$0.99 USD / item**).
  - Pembelian impulsif 1-klik via QRIS untuk skin visual eksklusif (misal: *Gundam Mecha, Retro Macintosh 1984, Vaporwave Sunset, RGB Reactive Chroma, & Custom Switch Audio Packs*).
* **Hardware Fisik DigiBoard OLED by King Ali Studio:**
  - **Macro Pad (12 Tuts OLED):** **Rp 1.499.000** ($99 USD) — *Bundling Lisensi Pro Seumur Hidup*.
  - **Full 65% OLED Workstation:** **Rp 3.499.000** ($229 USD) — *Bundling Lisensi Pro + Seluruh Paket Skin*.
* **Monetisasi Slot Stiker Palm Rest (Free Tier Ads & Affiliate):**
  - **Model Afiliasi:** Link diskon periferal tech, gaming gear, atau cloud/hosting di e-commerce (Tokopedia/Shopee/Amazon) dengan komisi 5% - 12% per penjualan.
  - **Sewa Slot Sponsor Brand:** Brand teknologi / gaming gear menyewa slot banner stiker tetap (misal: Rp 1.500.000 – Rp 3.000.000 / slot / bulan).
  - *Perk Pro:* Pengguna Pro All-Access bebas dari semua stiker sponsor (Clean Minimalist Deck) atau dapat menempelkan stiker kustom sendiri.
* **B2B / Lab License (Institusi / Kampus):** **Rp 999.000 / instansi** ($99.00 USD).

### C. Place (Distribusi Penjualan & Sentralisasi Menu Store)
* **Sentralisasi Menu "Store" di Dalam Aplikasi:**
  Seluruh item berbayar tidak tersebar secara acak, melainkan terpusat di satu wadah resmi: **Menu "Store"** (dapat diakses langsung dari Floating Deck dan pengaturan). Menu Store mengelompokkan:
  1. *Katalog Skin & Tema Premium:* Skin visual eksklusif (Gundam Mecha, Retro Mac 1984, Vaporwave, Cyberpunk Chroma) dan Custom Mechanical Audio Packs.
  2. *Katalog Plugin Pro:* Voice Typing (Speech-to-Text Dictation), Advanced AutoText Snippet Engine, AI Prompt Assistant, Macro Chaining.
  3. *Lisensi Pro All-Access:* Paket hemat seumur hidup membuka SEMUA skin dan SEMUA plugin selamanya.
  4. *Hardware Store (Pre-Order & Official Gear):* Showcase perangkat keras fisik resmi DigiBoard OLED Workstation Deck by King Ali Studio dengan link pre-order dan jaminan garansi resmi studio.
  5. *Tab Jalur Afiliasi (Partner Program):* Pintu pendaftaran instan bagi pengguna dan kreator untuk menjadi mitra penjual.
* **Distribusi Software:**
  - Kode & Versi Komunitas: **GitHub Releases**.
  - Checkout & Lisensi Pro (Global): **Gumroad** / **Lemon Squeezy** (menerima Kartu Kredit, Apple Pay, PayPal).
  - Checkout & Lisensi Pro (Indonesia): **Mayar** / **Lynk.id** / **Trakteer** (pembayaran QRIS instan, GoPay, OVO, Virtual Account).
* **PWA Deployment:** Hosted static web frontend di cloud/CDN untuk fallback.

### D. Promotion (Promosi, Jalur Afiliasi & Mesin Viralitas)
* **Jalur Afiliasi Terintegrasi (Affiliate & Virality Engine):**
  Untuk mendorong akselerasi penjualan dan viralitas tanpa biaya iklan awal yang mahal:
  - **Komisi Menarik:** Mitra afiliasi menerima **komisi 30% – 40%** untuk setiap penjualan Skin, Plugin Pro, maupun Lisensi Pro All-Access.
  - **Tautan Referral & Kupon Personal:** Setiap mitra mendapat URL unik (`digikeyboard.app/ref/nama_kreator`) dan kode promo diskon 10% untuk pengikutnya.
  - **Viral Loop Kreator (TikTok / Reels / Shorts):**
    1. Kreator membuat video demonstrasi visual (contoh: *"Mengetik suara di PC cuma ngomong ke HP"* atau *"Bikin tablet jadul jadi keyboard anime mecha"*).
    2. Tautan bio kreator mengarahkan langsung ke **Menu Store** DigiKeyboard.
    3. Penonton membeli item karena terbukti fungsional; kreator mendapatkan komisi otomatis; pembeli terdorong membagikan tautan referral miliknya ke teman atau komunitas.
* Mengutamakan kanal organik, konten video pendek demonstratif, dan komunitas teknis (dibedah di Bagian 4).

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
* **Fase 4: Ekspansi Hardware DigiBoard OLED by King Ali Studio (Bulan 4 s/d 6):**
  - Membuka kampanye Pre-Order / Crowdfunding terbatas (100–200 unit batch perdana) untuk keyboard fisik *DigiBoard OLED Workstation Deck*.
  - Mengirim unit prototipe fisik ke YouTuber reviewer keyboard mekanik & tech desk setup ternama untuk review viral.
  - Mengintegrasikan banner etalase hardware langsung di dalam Menu Store aplikasi DigiKeyboard.

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
