# 📈 Analisis Potensi Pasar & Proyeksi Penghasilan: DigiSmartDeck (AirDeck)

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
| **Lisensi Pro All-Access (Indonesia)** | **Rp 250.000** *(Promo: Rp 99k - 149k)* | ~Rp 6.250 (Mayar/Midtrans ~2.5%) | **Rp 243.750 (97%)** |
| **Lisensi Pro All-Access (Global)** | **$15.99 USD** (~Rp 250.000) | ~$1.30 (Lemon Squeezy 5% + $0.50) | **$14.69 (~Rp 230.000) (92%)** |
| **Skin & Theme Premium (Per Item)** | **Rp 10.000 / $0.99** | ~Rp 500 / $0.20 | **Rp 9.500 / $0.79 (95%)** |
| **Sewa Slot Stiker / Afiliasi (per bulan)** | **Rp 1.500.000 – Rp 3.000.000** | Net setelah fee / flat | **~Rp 1.500.000+ (100%)** |
| **Donasi Free Tier (Personal & Game)** | Sukarela (Rata-rata Rp 20.000) | ~Rp 1.000 (Saweria/Trakteer) | **Rp 19.000 (95%)** |
| **Lisensi B2B (Sekolah / Lab Komputer)** | **Rp 999.000 / $99.00** | ~Rp 25.000 / $5.50 | **Rp 974.000 / $93.50 (97%)** |

---

## 📊 3. Simulasi Proyeksi Pendapatan (Tahun Pertama - Harga Rp 250.000)

Dengan harga Rp 250.000 (blended average ~Rp 200.000 memperhitungkan promo early-bird), volume penjualan yang dibutuhkan untuk meraih ratusan juta rupiah jauh lebih sedikit:

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
│ • 150 Lisensi ID │          │ • 750 Lisensi ID │          │ • 2.500 Lis. ID  │
│ • 100 Lis. Int'l │          │ • 600 Lis. Int'l │          │ • 2.000 Lis. Int │
│ • 0 B2B Lab      │          │ • 5 B2B Lab      │          │ • 20 B2B Lab     │
├──────────────────┤          ├──────────────────┤          ├──────────────────┤
│  Rp 61,5 Juta    │          │   Rp 327,8 Juta  │          │  Rp 1,11 Miliar  │
│ (~$3.900 USD/th) │          │ (~$21.000 USD/th)│          │ (~$71.500 USD/th)│
│  Rp 5,1 Juta/bln │          │  Rp 27,3 Juta/bln│          │  Rp 92,8 Juta/bln│
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

### Rincian Simulasi Bertahap (Berdasarkan Akuisisi Pengguna 3 Tahap)

Struktur aliran pendapatan yang dihitung:
1. **Donasi Free Tier (Personal & Game)** (Tingkat donasi 0.1% - 0.3%)
2. **Mikrotransaksi Skin Kolektor @ Rp 10.000 / $0.99** (Konversi 2% - 5%)
3. **Monetisasi Stiker Palm Rest** (Komisi afiliasi periferal & sewa space sponsor brand)
4. **Lisensi Pro All-Access** (Harga normal Rp 250.000, blended average Rp 180k - 210k net)
5. **Lisensi B2B Kampus/Lab** (@ Rp 974.000 net)

---

#### 🌧️ Skenario PESIMIS (Pertumbuhan Organik Lambat / Tanpa Video Viral)

| Tahapan Akuisisi | Basis Pengguna Baru | Donasi | Skin Rp 10k | Stiker Ads / Afiliasi | Pro All-Access (Rp 250k) | Total Pendapatan Tahap | Rata-rata per Bulan |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tahap 1: Peluncuran (Bln 1–3)** | 5.000 user | Rp 100.000 | Rp 712.500 | Rp 300.000 | Rp 2.850.000 (30 unit promo) | **Rp 3.962.500** | ~Rp 1,3 Juta/bln |
| **Tahap 2: Traksi (Bln 4–6)** | 15.000 user | Rp 300.000 | Rp 2.850.000 | Rp 1.500.000 | Rp 21.600.000 (120 unit) | **Rp 26.250.000** | ~Rp 8,7 Juta/bln |
| **Tahap 3: Stabil (Bln 7–12)** | 40.000 user | Rp 800.000 | Rp 7.600.000 | Rp 9.000.000 (Afiliasi+Sewa) | Rp 69.100.000 (320 unit + 2 B2B) | **Rp 86.500.000** | ~Rp 14,4 Juta/bln |
| **TOTAL TAHUN 1 (PESIMIS)** | **60.000 user** | **Rp 1,2 Jt** | **Rp 11,1 Jt** | **Rp 10,8 Jt** | **Rp 93,5 Jt** | **Rp 116.712.500** | **~Rp 9,7 Juta/bulan** |

*Intisari Pesimis:* Sekalipun tanpa video viral, bisnis ini tetap membukukan laba bersih **~Rp 116 Juta di tahun pertama** (rata-rata ~Rp 10 Juta/bulan).

---

#### 🚀 Skenario OPTIMIS (Viralitas Game Mode & Streamer Adoption)

| Tahapan Akuisisi | Basis Pengguna Baru | Donasi | Skin Rp 10k | Stiker Ads / Afiliasi | Pro All-Access (Rp 250k) | Total Pendapatan Tahap | Rata-rata per Bulan |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tahap 1: Meledak (Bln 1–3)** | 25.000 user | Rp 1.500.000 | Rp 9.500.000 | Rp 2.500.000 | Rp 47.500.000 (500 unit promo) | **Rp 61.000.000** | ~Rp 20,3 Juta/bln |
| **Tahap 2: Viral FYP (Bln 4–6)** | 125.000 user | Rp 5.000.000 | Rp 59.375.000 | Rp 13.500.000 (Sewa brand + Afiliasi) | Rp 453.800.000 (2.250 unit + 4 B2B) | **Rp 531.675.000** | ~Rp 177,2 Juta/bln |
| **Tahap 3: Global Scale (Bln 7–12)**| 350.000 user | Rp 12.000.000| Rp 166.250.000| Rp 45.000.000 (2 brand sponsor eksklusif)| Rp 1.116.750.000 (5.250 unit + 15 B2B)| **Rp 1.340.000.000** | ~Rp 223,3 Juta/bln |
| **TOTAL TAHUN 1 (OPTIMIS)** | **500.000 user**| **Rp 18,5 Jt**| **Rp 235,1 Jt**| **Rp 61,0 Jt** | **Rp 1.618,0 Jt** | **Rp 1.932.675.000** | **~Rp 161,0 Juta/bulan** |

*Intisari Optimis:* Jika konten video Game Mode (misal setir gyro) menembus FYP TikTok/Shorts dan diadopsi komunitas streamer, pendapatan tahun pertama menembus **Rp 1,93 Miliar bersih** (~Rp 161 Juta/bulan).

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
