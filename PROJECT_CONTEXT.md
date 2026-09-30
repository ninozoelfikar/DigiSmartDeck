# DOKUMEN HANDOVER & KONTEKS PROYEK DIGIKEYBOARD
File ini dibuat untuk memastikan keberlanjutan pengembangan tanpa kehilangan progres atau konteks saat beralih akun Antigravity, sesi chat baru, atau pengembang baru.

---

## 1. PANDUAN CEPAT UNTUK ASISTEN / AGENT BARU
Jika Anda adalah AI Agent baru yang membaca repositori ini untuk pertama kali:
1. Baca dokumen ini dari awal hingga akhir sebelum menulis atau mengubah kode.
2. Periksa status git saat ini:
   - Branch aktif: `test/concept-a-deck`
   - File utama: `server.py` (backend Python aiohttp), `static/index.html` (frontend tunggal vanilla JS/CSS).
3. Aturan mutlak:
   - DILARANG menggunakan emoticon atau emoji dalam bentuk apa pun di seluruh kode, log terminal, antarmuka UI, maupun respons chat.
   - Efek suara klik mekanikal (`playClickSound()`) pada tombol interaktif harus selalu dipertahankan.
   - File instalasi aplikasi ponsel Android (`DigiKeyboard.apk`) harus tetap sangat ringan (~20 MB). Tidak boleh membundel model AI ke dalam APK ponsel.
   - Setelah menyelesaikan tugas, asisten cukup merespons dengan 'Selesai' atau 'Done', KECUALI jika pengguna secara eksplisit meminta penjelasan.
4. Server berjalan sebagai layanan systemd Linux:
   - Nama layanan: `digikeyboard.service`
   - Restart server dengan perintah: `pkill -f "/home/nino/digikeyboard/server.py"` (systemd otomatis me-restart proses baru dalam 3 detik).
   - Cek log server: `journalctl -u digikeyboard -n 30 --no-pager`

---

## 2. TUJUAN BISNIS & MODEL KOMERSIAL
- Nama Produk: DigiKeyboard
- Fungsi: Pengendali keyboard, touchpad, gamepad, dan deck pintasan AI untuk PC berbasis perangkat ponsel/tablet melalui jaringan lokal (Wi-Fi dan kabel USB).
- Model Monetisasi: Perangkat lunak komersial berbayar (SaaS):
  - Paket Langganan: Rp 15.000 per bulan
  - Paket Lisensi Seumur Hidup (Lifetime): Rp 250.000
- Nilai Jual Utama (USP) di AI Workstation:
  - Dikte suara profesional untuk menyusun prompt ChatGPT, Claude, atau perintah terminal.
  - Mikrofon tidak mati otomatis saat pengguna berhenti bicara untuk berpikir.
  - Bebas dari bunyi notifikasi/chime sistem Android yang mengganggu alur ide pengguna.
  - Respon latensi sangat rendah.

---

## 3. RIWAYAT PERKEMBANGAN & SOLUSI TEKNIS

### Masalah Awal pada Mic Browser (Google Web Speech API)
- Google Chrome di Android menggunakan layanan Google Speech Service bawaan sistem operasi.
- Batasan Google:
  1. *Silence timeout* dikunci secara *hardcoded* pada 3 hingga 5 detik. Jika pengguna hening untuk berpikir, mic otomatis mati sendiri.
  2. Sistem Android otomatis membunyikan suara bel/ding (*system chime*) setiap kali mic menyala atau mati. Ini menimbulkan bunyi berulang-ulang saat jeda berpikir.
  3. Terjadi gema atau duplikasi kata saat browser mengirim chunk transkripsi berulang.

### Solusi yang Telah Dibangun (Mode Local Pro AI Mic)
1. **Penangkapan Audio Murni:**
   - Menggunakan `navigator.mediaDevices.getUserMedia` standar WebRTC.
   - Android TIDAK PERNAH membunyikan chime apa pun saat `getUserMedia` aktif.
   - Mikrofon mendengarkan terus-menerus tanpa batas waktu hingga tombol ditekan kembali oleh pengguna.
2. **Mesin Transkripsi Lokal (OpenAI Whisper via faster-whisper):**
   - Backend menggunakan `faster-whisper` (CTranslate2) pada CPU PC host (Intel Core i5-11400F, 6 thread int8).
   - Model yang terpasang dan dicache di disk: `small` (244 juta parameter, ukuran ~240 MB int8, waktu load 0.77 detik).
   - Parameter decoding presisi:
     - `beam_size=5` (multi-path search)
     - `best_of=5`
     - `temperature=0.0` (deterministik tanpa halusinasi)
     - `condition_on_previous_text=False` (mencegah akumulasi salah dengar)
     - `vad_filter=True` dengan Silero VAD (`speech_pad_ms=400`)
     - `initial_prompt="Dikte kalimat bahasa Indonesia dengan ejaan yang benar dan jelas."`
3. **Pengaturan Jeda Berpikir (VAD Client):**
   - Jeda hening diatur sebesar 2.2 detik (2200 ms). Pengguna bebas mengambil napas atau berpikir hingga 2 detik tanpa kalimat terpotong di tengah jalan.
   - Audio dikirim dengan bitrate 128 kbps dan penekan derau browser dinonaktifkan (`noiseSuppression: false`) agar konsonan halus (s, t, p, k) tidak diredam.

---

## 4. KEPUTUSAN PRODUK: PENETAPAN METODE TUNGGAL (GOOGLE SPEECH)
Berdasarkan uji coba langsung dan instruksi pengguna:
1. Metode alternatif (Whisper AI Mic lokal) dan konfigurasi dual-port (8081) telah dihapus sepenuhnya dari kode.
2. DigiKeyboard kini menggunakan SATU metode tunggal untuk dikte suara: **Google Web Speech API**.
3. Tombol pemilihan engine di antarmuka (`[Google]` vs `[AI Mic]`) telah dihilangkan agar tampilan bersih, intuitif, dan tidak membingungkan pengguna.
4. Nilai keunggulan dari arsitektur tunggal ini:
   - Antarmuka sangat simpel (*zero clutter*): hanya ada tombol Mic utama, pemilih bahasa (ID / EN), dan Auto-Kirim.
   - Penggunaan RAM server PC host turun drastis dari ~554 MB menjadi hanya ~31 MB.
   - Kecepatan startup server instan (< 0.1 detik).
   - Pengenalan kata bahasa Indonesia langsung muncul kata demi kata secara real-time (*streaming interim results*).
   - Biaya 0 rupiah dan bebas lisensi komputasi model AI untuk produk SaaS (Rp 15.000/bln atau Rp 250.000 lifetime).

---

## 5. PENGALAMAN PENGGUNA & ARSITEKTUR KLIEN
- Port tunggal standar: **8080** (baik via Wi-Fi lokal maupun kabel USB via ADB reverse).
- Klien komersial (pembeli APK Android) tidak perlu menyetel port di `chrome://flags` karena aplikasi Android resmi (`DigiKeyboard.apk`) menggunakan WebView dengan izin mikrofon internal native.
- Sesi dikte berhenti secara wajar saat jeda hening tanpa memicu bunyi notifikasi berulang-ulang.
- Efek suara klik mekanikal (`playClickSound()`) selalu dipertahankan di setiap interaksi tombol.
- Tombol `ENTER` di AI Workstation selalu mengirim teks transkrip ke PC, mengeksekusi Enter di PC, dan mengosongkan box di ponsel dalam satu ketukan efisien.
- Tombol pintasan prompt instan (`Lanjutkan`, `Proceed`, `Perbaiki Bug`, `Buat Dokumen`, `Jadikan Check Point`) otomatis mengetik teks ke PC dan langsung mengeksekusi Enter tanpa perlu menekan tombol tambahan.
- Kolom kiri AI Workstation menampung tombol editing (`Copy`, `Paste`, `Esc`, `Tab`, `Backspace`, `Delete`) dan pintasan prompt yang terbagi merata dalam 7 baris (`repeat(7, 1fr)`).
- Kolom kanan AI Workstation mengisi tinggi layar secara penuh dan proporsional: Tombol Enter (~40%), Navigasi Riwayat & Kursor (~20%), serta Trackpad (~40%) yang mendukung gerakan kursor dan tap untuk klik kiri.
- Header AI Workstation dilengkapi tombol `Fullscreen` dan `Reload` untuk kemudahan pengujian selama pengembangan di browser ponsel sebelum perilisan versi APK.

---

## 6. STRUKTUR FILE REPOSITORI
- `server.py`: Server web aiohttp berkecepatan tinggi, endpoint WebSocket (`/ws`), penanganan simulasi input Linux uinput/pynput.
- `static/index.html`: Berkas tunggal antarmuka web, mencakup CSS deck, keyboard virtual, touchpad, gamepad, presentasi, dan AI Workstation (Google Web Speech).
- `requirements.txt`: Dependensi Python (`aiohttp`, `evdev`, `pynput`, `qrcode`).
- `digikeyboard.service`: File konfigurasi systemd unit di `/etc/systemd/system/digikeyboard.service`.
- `build-apk.sh` & `android/`: Proyek WebView Android untuk kompilasi APK mandiri.

---

## 7. CATATAN CHECKPOINT TERBARU (v0.9.3 - Reconnect Modal & Ghost Mode Switcher)
- **Modal Reconnecting Berlayar Redup (Fullscreen Dim Overlay):**
  - Banner reconnecting di atas layar telah diganti dengan modal pop-up elegan di tengah layar (`width: min(450px, 92vw)`).
  - Layar sepenuhnya terblokir secara halus dengan efek redup (`background: rgba(10, 12, 16, 0.85); backdrop-filter: blur(6px)`) saat sambungan terputus.
  - Pilihan tombol hanya dua yang esensial dan bekerja pasti: `Coba Lagi` dan `Mode USB`. Tombol bantuan dan close yang tidak fungsional telah dihapus untuk mencegah kebingungan pengguna amatir. Teks tombol dilindungi dengan `white-space: nowrap !important` sehingga tidak pernah terpotong 2 baris.
- **Shortcut Mode Kerja Mengambang (Ghost Tab Header):**
  - Empat ikon mode (Keyboard PC, Game Console, Slide Remote, AI Workstation) dipindahkan ke bar atas sebelah kanan tepat di samping kiri menu sandwich.
  - Tampilan ikon dibuat bersih tanpa kotak (*borderless / ghost icons*), dengan ikon aktif menyala terang dan memiliki garis aksen bawah (*active underline indicator*).
- **Penyempurnaan Tata Letak AI Workstation:**
  - Tombol Mic utama telah diperbesar proporsional (86px pada base view, 64px pada landscape compact).
  - Teks petunjuk panjang di bawah mic telah dihapus untuk mengoptimalkan ruang vertikal.
  - Tombol `Bersihkan` dan `Kirim ke PC` diperbesar 30% dengan font 12.5px.
  - Checklist `Auto-Kirim` dipindahkan ke sisi kiri footer kolom transkrip berdampingan dengan tombol aksi.

