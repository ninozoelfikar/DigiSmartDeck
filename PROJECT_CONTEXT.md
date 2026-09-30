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

## 4. TUGAS AKTIF SAAT INI (DUAL-PORT BENCHMARK 8080 & 8081)
Pengguna meminta pembuatan dua kondisi pembanding secara berdampingan untuk menguji performa presisi:
- **Port 8080:** Edisi Whisper AI Mic (Sistem mic lokal mandiri, bebas bunyi, bebas timeout).
- **Port 8081:** Edisi Google Speech (Sistem Web Speech API bawaan Google).

### Desain Arsitektur Dual-Port:
1. `server.py` menjalankan satu proses aiohttp yang mendengarkan pada dua port TCP sekaligus:
   - `web.TCPSite(runner, '0.0.0.0', 8080)`
   - `web.TCPSite(runner, '0.0.0.0', 8081)`
2. `adb_reverse_watcher` membuka port forwarding untuk kedua port (`8080` dan `8081`) agar koneksi kabel USB tetap berfungsi pada kedua alamat.
3. Klien frontend (`static/index.html`):
   - Jika diakses via `http://[IP]:8080`: Otomatis mengaktifkan engine `whisper` sebagai default. Badge menampilkan: `AI WORKSTATION - WHISPER AI MIC (PORT 8080)`.
   - Jika diakses via `http://[IP]:8081`: Otomatis mengaktifkan engine `browser` sebagai default. Badge menampilkan: `AI WORKSTATION - GOOGLE SPEECH (PORT 8081)`.
   - Pada Port 8081 (Google Speech), mic sengaja diatur berhenti secara natural saat hening (tanpa auto-restart paksa), sehingga tidak menimbulkan chime berulang-ulang dan dapat dibandingkan secara murni dengan Port 8080 (Whisper AI Mic).
   - Pengguna dapat membuka kedua URL di tab browser terpisah untuk membandingkan akurasi kalimat dan kenyamanan jeda secara langsung.

---

## 5. KEPUTUSAN PRODUK: PENGGUNAAN METODE GOOGLE SPEECH
Berdasarkan uji coba perbandingan langsung antara model lokal Whisper dan Google Speech:
1. Pengguna secara definitif memutuskan untuk menggunakan metode Google (Web Speech API) sebagai mesin dikte utama DigiKeyboard.
2. Alasan keputusan:
   - Akurasi pengenalan kata dan ejaan bahasa Indonesia Google Speech sangat presisi dan matang.
   - 0% beban ukuran model dan RAM di komputer pengguna (sangat ideal untuk software komersial SaaS berbayar Rp 15.000/bln atau Rp 250.000 seumur hidup).
   - Biaya 0 rupiah (menggunakan layanan speech bawaan browser tanpa langganan API berbayar).
3. Penyempurnaan UX yang telah diterapkan:
   - Loop auto-restart paksa telah dinonaktifkan sepenuhnya. Sesi Google Speech kini berhenti secara wajar dan bersih saat hening tanpa memicu chime berulang-ulang.
   - Saat pengguna ingin lanjut berbicara, pengguna cukup mengetuk tombol mic kembali dengan respons bunyi klik mekanikal yang memuaskan (`playClickSound()`).
   - Algoritma `mergeTranscripts` mencegah gema atau pengulangan kata saat dikte disambung.
   - Mode utama di Port 8080 telah disetel default ke Google Speech. Tombol toggle `[Google]` dan `[AI Mic]` tetap tersedia jika sewaktu-waktu ingin beralih.

---

## 6. STRUKTUR FILE REPOSITORI
- `server.py`: Server web aiohttp, endpoint WebSocket (`/ws`), penanganan simulasi input Linux uinput/pynput, dan transkripsi Whisper.
- `static/index.html`: Berkas tunggal antarmuka web, mencakup CSS deck, keyboard virtual, touchpad, gamepad, presentasi, dan AI Workstation.
- `requirements.txt`: Dependensi Python, mencakup `aiohttp`, `faster-whisper>=1.0.0`, `av<14` (13.1.0).
- `digikeyboard.service`: File konfigurasi systemd unit di `/etc/systemd/system/digikeyboard.service`.
- `build-apk.sh` & `android/`: Proyek WebView Android untuk kompilasi APK mandiri.
