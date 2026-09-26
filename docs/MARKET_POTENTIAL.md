# 📈 Analisis Potensi Pasar & Proyeksi Penghasilan: DigiKeyboard (AirDeck)

---

## 🌐 1. Pemetaan Ukuran Pasar (TAM, SAM, SOM)

Perhitungan potensi pasar didasarkan pada populasi pengguna PC/Laptop aktif yang memiliki smartphone/tablet serta berada dalam ceruk kebutuhan kendali nirkabel, perbaikan darurat, atau produktivitas workstation.

```
┌────────────────────────────────────────────────────────────────────────┐
│  TAM: Total Addressable Market (Global & Domestik)                     │
│  • Global: 1,5 Miliar PC aktif di dunia                                │
│  • Indonesia: ~28 Juta pengguna PC/Laptop                              │
│  Nilai Pasar Global Software Utilitas Remote/Peripheral: ~$2,4 Miliar   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  SAM: Serviceable Addressable Market (Target Relevan)                  │
│  SysAdmin, Homelabber, Pekerja Remote, Pemilik HTPC, Streamer/Creator  │
│  • Pasar Global: ~45 Juta pengguna potensial                           │
│  • Pasar Indonesia: ~1,8 Juta pengguna potensial                       │
│  Nilai Valuasi SAM: ~$180 Juta USD                                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  SOM: Serviceable Obtainable Market (Target Realistis Tahun 1-2)       │
│  Pangsa Pasar Tergapai (Penetrasi 0,02% - 0,05% dari SAM):             │
│  • Pasar Global: 10.000 – 25.000 pembeli                               │
│  • Pasar Indonesia: 3.000 – 10.000 pembeli                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 💰 2. Unit Economics & Struktur Harga

Produk software utilitas lokal memiliki keunggulan ekstrem: **beban server mendekati Rp 0**, karena transmisi WebSocket berjalan di jaringan Wi-Fi lokal pengguna (peer-to-peer lokal).

| Produk / Aliran Pendapatan | Harga Jual Kotor (Gross) | Potongan Biaya Payment Gateway | Pendapatan Bersih per Unit (Net Margin) |
| :--- | :--- | :--- | :--- |
| **Lisensi Pro (Indonesia - QRIS/E-Wallet)** | **Rp 49.000** | ~Rp 1.500 (Mayar / Midtrans ~2.5% + fee) | **Rp 47.500 (97%)** |
| **Lisensi Pro (Global - Kartu Kredit/PayPal)** | **$4.99 USD** (~Rp 78.000) | ~$0.75 (Lemon Squeezy 5% + $0.50) | **$4.24 (~Rp 66.000) (85%)** |
| **Preset Macro / Theme Pack (Add-on)** | **Rp 25.000 / $1.99** | ~Rp 1.000 / $0.40 | **Rp 24.000 / $1.59 (96%)** |
| **Lisensi B2B (Sekolah / Lab Komputer)** | **Rp 499.000 / $49.00** | ~Rp 15.000 / $3.50 | **Rp 484.000 / $45.50 (97%)** |

---

## 📊 3. Simulasi Proyeksi Pendapatan (Tahun Pertama)

Berikut adalah 3 skenario pendapatan tahunan berdasarkan intensitas eksekusi pemasaran:

```
          ┌─────────────────────────────────────────────────────────┐
          │        PROYEKSI PENDAPATAN BERSIH TAHUNAN (TAHUN 1)     │
          └────────────────────────────┬────────────────────────────┘
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│   KONSERVATIF    │          │     MODERAT      │          │     AGRESIF      │
│  (Side-Project)  │          │   (Realistis)    │          │  (Viral Scale)   │
├──────────────────┤          ├──────────────────┤          ├──────────────────┤
│ • 500 Lisensi ID │          │ • 2.500 Lis. ID  │          │ • 8.000 Lis. ID  │
│ • 300 Lis. Int'l │          │ • 1.800 Lis. Int │          │ • 6.500 Lis. Int │
│ • 0 B2B Lab      │          │ • 10 B2B Lab     │          │ • 35 B2B Lab     │
├──────────────────┤          ├──────────────────┤          ├──────────────────┤
│  Rp 48,5 Juta    │          │   Rp 276,4 Juta  │          │   Rp 914,8 Juta  │
│ (~$3.100 USD/th) │          │ (~$17.700 USD/th)│          │ (~$58.600 USD/th)│
│  Rp 4 Juta/bulan │          │  Rp 23 Juta/bulan│          │  Rp 76 Juta/bulan│
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

### Rincian Simulasi:

#### Skenario 1: Konservatif (Pertumbuhan Organik Murni / Tanpa Iklan)
*Kondisi: Hanya mengandalkan repository GitHub, rilis Reddit sekali, dan word-of-mouth pengguna Linux/Homelab.*
* **Lisensi Pro Indonesia:** 500 unit × Rp 47.500 = Rp 23.750.000
* **Lisensi Pro Global:** 300 unit × Rp 66.000 = Rp 19.800.000
* **Donasi FOSS / Sponsors (GitHub/Saweria):** Rp 5.000.000
* **Total Pendapatan Bersih:** **Rp 48.550.000 / tahun** *(~Rp 4.000.000 / bulan)*.

---

#### Skenario 2: Moderat (Rekomendasi Baseline - Eksekusi Rencana Pemasaran)
*Kondisi: Binary Windows .exe 1-klik siap, Product Hunt Top 5, 2–3 konten video TikTok/Shorts tembus FYP (>100k views), promosi rutin di grup tech.*
* **Lisensi Pro Indonesia:** 2.500 unit × Rp 47.500 = **Rp 118.750.000**
* **Lisensi Pro Global:** 1.800 unit × Rp 66.000 = **Rp 118.800.000**
* **Add-on Theme & Macro Packs (Take-rate 20%):** 860 unit × Rp 24.000 = **Rp 20.640.000**
* **Lisensi B2B / Lab Komputer Kampus/Sekolah:** 10 paket × Rp 484.000 = **Rp 4.840.000**
* **Donasi & Sponsorship:** Rp 13.400.000
* **Total Pendapatan Bersih:** **Rp 276.430.000 / tahun** *(~Rp 23.000.000 / bulan)*.

---

#### Skenario 3: Agresif (Pertumbuhan Cepat / Viral & Ekspansi Produk)
*Kondisi: Di-review oleh channel tech besar (YouTuber/TikToker setup desk), adopsi luas di kalangan gamer dan pemilik TV PC, integrasi hardware dongle ESP32.*
* **Lisensi Pro Indonesia:** 8.000 unit × Rp 47.500 = **Rp 380.000.000**
* **Lisensi Pro Global:** 6.500 unit × Rp 66.000 = **Rp 429.000.000**
* **Add-on Theme & Macro Packs:** 2.800 unit × Rp 24.000 = **Rp 67.200.000**
* **Lisensi B2B Institusi:** 35 paket × Rp 484.000 = **Rp 16.940.000**
* **Penjualan Hardware Dongle USB (Plug & Play):** 300 unit × Laba Bersih Rp 75.000 = **Rp 22.500.000**
* **Total Pendapatan Bersih:** **Rp 915.640.000 / tahun** *(~Rp 76.300.000 / bulan)*.

---

## 📉 4. Biaya Operasional (OpEx) & Net Margin

Karena tidak ada biaya infrastruktur server cloud yang mahal (pengguna menjalankan server di PC masing-masing), struktur laba bersih produk ini sangat tebal:

| Pos Biaya | Estimasi Biaya per Tahun |
| :--- | :--- |
| Domain Landing Page (`.app` / `.dev`) | Rp 250.000 |
| Cloudflare Pages / Static Hosting | Rp 0 (Free Tier) |
| Sertifikat Code Signing Windows (Opsional agar tidak ada peringatan SmartScreen) | Rp 1.800.000 |
| Biaya Pemasaran / Seed Konten Kreator | Rp 3.000.000 |
| **Total Estimasi Biaya Tahunan** | **~Rp 5.050.000** |

> **Profit Margin:** **90% – 95%**. Hampir seluruh pendapatan kotor setelah fee payment gateway langsung menjadi laba bersih (*pure cash flow*).

---

## 🎯 5. Kesimpulan Strategis

1. **Titik Impas (BEP) Instan:** Dengan modal peluncuran awal yang sangat minim (< Rp 3.000.000), titik impas (*Break-Even Point*) tercapai hanya dengan menjual **65 lisensi Pro**.
2. **Karakteristik Cash-Cow:** Produk ini adalah tipikal software *micro-SaaS / digital utility* yang berpotensi menjadi sumber *passive income* berkisar **Rp 20.000.000 – Rp 75.000.000 per bulan** dengan biaya pemeliharaan (*maintenance overhead*) yang sangat rendah setelah rilis stabil.
3. **Kunci Penentu Pendapatan:** Perbedaan antara skenario Konservatif (Rp 48 Juta) dan Moderat (Rp 276 Juta) hanya terletak pada **ketersediaan installer mandiri (.exe)** dan **video demonstrasi pendek yang viral**.
