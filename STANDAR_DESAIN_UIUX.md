# STANDAR DESAIN UI/UX & REKAYASA APLIKASI
### Berbasis Pembelajaran & Studi Kasus Proyek DigiSmartDeck
Dokumen master tersimpan di Obsidian Vault: `[[Referensi/Standar Desain dan Rekayasa Aplikasi - Studi Kasus DigiSmartDeck]]`

---

## 1. PRINSIP DESAIN UI/UX & ERGONOMI SENTUH (TOUCH ERGONOMICS)

### 1.1. Kejelasan Status Visual (Visual State Clarity)
- **Masalah:** Pada antarmuka virtual biasa, pengguna sering bingung melihat tombol yang memiliki dua label karakter bertumpuk (misal angka 1 dan tanda seru !). Saat tombol Shift ditekan, tampilan tidak berubah sehingga memicu keraguan apakah karakter alternatif sudah aktif.
- **Standar Solusi (Dynamic Character Layer):**
  - Saat tombol pengubah (seperti Shift) aktif, ubah antarmuka secara eksklusif: sembunyikan karakter dasar dan tampilkan **hanya** karakter alternatif dalam ukuran penuh dan rata tengah.
  - Ini meniru kealamian metode pergantian huruf besar dan huruf kecil (QWERTY), menghilangkan beban kognitif pengguna saat mengetik.
  - Saat tombol pengubah dilepas, kembalikan tampilan dasar dan sub-label secara instan dan mulus.

### 1.2. Umpan Balik Taktil & Suara (Multisensory Feedback)
- **Masalah:** Layar sentuh kaca (*flat glass*) tidak memiliki umpan balik fisik, sehingga mengetik atau menekan kontrol virtual sering terasa hambar dan memicu salah ketik (*miss-click*).
- **Standar Solusi:**
  - Kombinasikan suara klik instan mekanikal (`playClickSound()`) dengan getaran mikro haptik (`vibe(12ms)`).
  - Hilangkan delay bawaan browser seluler (300ms tap delay) menggunakan event `touchstart` atau `pointerdown` dengan opsi `{ passive: true }`.
  - Pasang visual latch (gaya tombol tertekan atau garis indikator aktif) agar mata pengguna segera mendapat konfirmasi bahwa perintah telah tereksekusi.

### 1.3. Desain Suara Psikologis & Startup Jingle (Acoustic Psychology)
- **Masalah:** Suara aplikasi sering dianggap remeh atau hanya menggunakan efek audio generator generik/metronomik yang terdengar kaku seperti komputer, atau bahkan tidak ada identitas suara saat startup.
- **Standar Solusi:**
  - **Identitas Suara Organik:** Gunakan suara dari instrumen kontrol aplikasi itu sendiri (misalnya suara ketukan mekanikal keyboard asli).
  - **Kadens Irama Alami Manusia:** Hindari tempo metronomik yang konstan. Gunakan variasi ritme manusia (misal: 2 ketukan cepat, jeda 1 ketukan, 1 ketukan jeda hening, lalu 2 ketukan berjarak) dengan mikro-variasi tempo antar ketukan layaknya pergantian tangan kiri dan kanan.
  - **Progresi Nada Naik (Ascending Energy Boost):** Akhiri jingle startup pada nada yang tinggi dan renyah. Secara psikologis, progresi nada yang menanjak memicu optimisme, antusiasme, dan kenaikan energi positif bagi pengguna yang baru hendak memulai sesi kerja.
  - **Pemisahan Resonansi Bodi dan Klik:** Saat memodulasi nada (pitch), naikkan frekuensi transien klik secara cerah, namun pertahankan frekuensi resonansi bodi pada rentang rendah (85Hz-100Hz) agar suara tetap padat, tebal, dan tergrounding mantap tanpa melengking tipis.

### 1.4. Isolasi Event pada Bidang Interaktif Kustom (Event Isolation)
- **Masalah:** Permukaan seperti Canvas atau Trackpad biasanya menangkap seluruh event touch/mouse dengan `e.preventDefault()`. Ketika kita menambahkan kontrol overlay seperti tombol gear, slider pengaturan, atau toggle di atasnya, event kontrol tersebut ikut terbajak dan mengirim input yang salah ke sistem utama.
- **Standar Solusi:**
  - Terapkan fungsi filter deteksi target kontrol (misal: `isTpEditorTarget(e)`).
  - Jika target interaksi berasal dari kontrol editor internal, hentikan propagasi atau bypass `preventDefault` bidang utama sehingga slider dan toggle dapat digeser mulus tanpa menggerakkan kursor atau memicu klik liar.

### 1.5. Penyimpanan Pengaturan Real-Time Tanpa Tombol Simpan (Zero-Click Persistence)
- **Masalah:** Tombol "Save" atau "Apply" di panel pengaturan menciptakan friksi. Pengguna sering lupa menekan tombol simpan dan setelannya hilang saat aplikasi dimuat ulang.
- **Standar Solusi:**
  - Setiap perubahan toggle, slider, tata letak, dan status baris panel harus langsung tersimpan ke `localStorage` pada event `change` atau `input`.
  - Pada inisialisasi aplikasi dan saat berpindah antar mode kerja, lakukan restorasi state secara otomatis (`restoreKeyboardPanels()`).

---

## 2. STANDAR ARSITEKTUR PERANGKAT LUNAK & PERFORMA TINGGI

### 2.1. Efisiensi Ekstrem: Klien Super Ringan (~20 MB)
- **Prinsip Beban Komputasi:**
  - Klien di ponsel pintar/tablet harus mempertahankan ukuran instalasi sekecil mungkin (~20 MB APK).
  - Dilarang membundel model AI berat (seperti Whisper, LLM, atau model neural besar) ke dalam paket aplikasi klien seluler.
  - Alihkan seluruh beban komputasi berat ke host server PC atau gunakan API bawaan sistem operasi (seperti Web Speech API native browser/WebView).
- **Hasil Terbukti di DigiSmartDeck:**
  - Penggunaan RAM server turun drastis dari ~554 MB menjadi hanya ~31 MB.
  - Waktu startup aplikasi menjadi instan (< 0.1 detik).

### 2.2. Sintesis Audio Prosedural (Web Audio API) vs File Aset Audio
- **Prinsip Zero Asset Overhead:**
  - Hindari membundel berkas media statis seperti `.mp3` atau `.wav` jika suara dapat disintesis secara prosedural.
  - Menggunakan osilator Web Audio API (`triangle` untuk klik tajam, `sine` untuk dentuman bodi, dan `exponentialRampToValueAtTime` untuk peluruhan cepat) menghasilkan:
    1. Bobot file 0 byte (menghemat ukuran APK dan bandwidth).
    2. Respon instan tanpa latensi decoding file audio.
    3. Bebas dari galat aset hilang (404 Not Found) atau masalah caching.
    4. Kemampuan memodulasi pitch, volume, dan kecepatan secara matematis dan real-time.

### 2.3. Sistem Pemulihan Sambungan Mandiri (Self-Healing Network Architecture)
- **Prinsip Ketahanan Jaringan:**
  - Jaringan nirkabel lokal (Wi-Fi) rentan terhadap fluktuasi sinyal, mode hemat baterai ponsel, atau perpindahan jaringan.
  - Terapkan mekanisme heartbeat (*ping-pong*) setiap 3000ms dan pengawas mandiri (*watchdog timer*).
  - Tampilkan modal rekoneksi berlayar redup (*fullscreen dim overlay*) dengan animasi radar pulse elegan yang memindai multi-kanal secara otomatis (Wi-Fi LAN, Kabel USB ADB reverse, QR Scan) tanpa memaksa pengguna mengklik tombol secara manual.

### 2.4. Akselerasi Hapus Bertingkat (Adaptive Multi-Tier Deletion Engine)
- **Prinsip Kecepatan Kerja:**
  - Tombol penghapus standar sering kali terlalu lambat jika harus menghapus teks panjang, atau sebaliknya terlalu agresif sehingga menghapus tulisan yang tidak sengaja terhapus.
  - Solusi Multi-Tier:
    - 1x tap & tahan: menghapus karakter demi karakter (interval 60ms).
    - 2x tap & tahan: menghapus kata demi kata (interval 140ms).
    - 3x tap & tahan: menghapus blok 5 kata (interval 240ms).
  - Reset hitungan ketukan secara otomatis setelah jeda hening 400ms.

---

## 3. DISIPLIN REKAYASA & PENGEMBANGAN BERPASANGAN DENGAN AI AGENT

### 3.1. Kebersihan Kode & Nol Emoji (Strict Zero Emojis / Zero Emoticons)
- Dilarang memasukkan emoji atau emotikon ke dalam kode sumber, commit message, log terminal, antarmuka UI, maupun respons chat internal.
- Menjaga repositori tetap profesional, bersih, mudah diparsing oleh parser skrip CLI Linux, dan bebas dari masalah encoding UTF-8 pada berbagai emulator terminal.

### 3.2. Single Source of Truth Context Handover (`PROJECT_CONTEXT.md`)
- Setiap kali checkpoint fitur selesai, dokumentasikan detail keputusan teknis, arsitektur, parameter angka, dan batasan produk ke dalam berkas handover proyek.
- Hal ini menjamin bahwa saat berpindah sesi chat, berganti akun, atau bertukar developer, tidak ada konteks atau fitur yang hilang maupun terduplikasi.

### 3.3. Siklus Verifikasi Wajib Sebelum Menyatakan Tugas Selesai
1. **Pemeriksaan Sintaks Mandiri:** Jalankan validator sintaks (misal `node -c` untuk JavaScript dan `python3 -m py_compile` untuk skrip backend).
2. **Pemeriksaan Status Layanan Sistem:** Pastikan service latar belakang (seperti `systemctl status digikeyboard.service`) aktif dan proses baru berjalan normal setelah restart.
3. **Pemeriksaan Git Working Tree:** Jalankan `git status` dan pastikan seluruh perubahan telah ter-commit bersih pada branch kerja aktif.
4. **Respon Pasca-Tugas Minimalis:** Jika tugas berhasil diselesaikan dan pengguna tidak meminta penjelasan, asisten cukup merespons dengan satu kata padat: `Selesai.`

---

## 4. CHECKLIST PRA-PENGEMBANGAN FITUR BARU UNTUK PROYEK MENDATANG

- [ ] **Ergonomi Sentuh:** Apakah ukuran elemen interaktif minimal 44x44px untuk jempol/jari?
- [ ] **Umpan Balik:** Apakah ada feedback visual (warna/latch), audio (klik), dan haptik (vibrasi) instan?
- [ ] **Kejelasan Status:** Apakah tombol hanya menampilkan opsi/karakter yang relevan dengan status aktif saat ini?
- [ ] **Penyimpanan:** Apakah preferensi pengguna langsung tersimpan ke penyimpanan lokal tanpa perlu tombol simpan?
- [ ] **Ringan & Cepat:** Apakah fitur ini menambah dependensi berat yang sebenarnya bisa dibuat dengan Web Standards native?
- [ ] **Penanganan Galat:** Bagaimana perilaku UI saat koneksi terputus atau API gagal merespons?
- [ ] **Dokumentasi:** Apakah perubahan ini sudah dicatat di file konteks proyek untuk keberlanjutan sesi berikutnya?
