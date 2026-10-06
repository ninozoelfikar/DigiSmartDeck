# DOKUMEN HANDOVER & KONTEKS PROYEK DIGISMARTDECK
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
   - File instalasi aplikasi ponsel Android (`DigiSmartDeck.apk`) harus tetap sangat ringan (~20 MB). Tidak boleh membundel model AI ke dalam APK ponsel.
   - Setelah menyelesaikan tugas, asisten cukup merespons dengan 'Selesai' atau 'Done', KECUALI jika pengguna secara eksplisit meminta penjelasan.
4. Server berjalan sebagai layanan systemd Linux:
   - Nama layanan: `digikeyboard.service`
   - Restart server dengan perintah: `pkill -f "/home/nino/digikeyboard/server.py"` (systemd otomatis me-restart proses baru dalam 3 detik).
   - Cek log server: `journalctl -u digikeyboard -n 30 --no-pager`

---

## 2. TUJUAN BISNIS & MODEL KOMERSIAL
- Nama Produk: DigiSmartDeck
- Fungsi: Pengendali keyboard, touchpad, gamepad, dan deck pintasan AI untuk PC berbasis perangkat ponsel/tablet melalui jaringan lokal (Wi-Fi dan kabel USB).
- Model Monetisasi: Perangkat lunak komersial berbayar (SaaS):
  - Paket Langganan: Rp 25.000 per bulan
  - Paket Lisensi Seumur Hidup (Lifetime): Rp 250.000
- Nilai Jual Utama (USP) di AI Workstation & Controller:
  - Dikte suara profesional untuk menyusun prompt ChatGPT, Claude, atau perintah terminal.
  - Mikrofon tidak mati otomatis saat pengguna berhenti bicara untuk berpikir.
  - Bebas dari bunyi notifikasi/chime sistem Android yang mengganggu alur ide pengguna.
  - Respon latensi sangat rendah (<1ms via USB, <15ms via Wi-Fi).
  - Privasi & Keamanan Murni Jaringan Lokal (Zero-Telemetry & Air-Gapped Ready):
    * Nol Perekaman Input (Zero Keystroke Logging): Input keyboard, password, dan teks suara dieksekusi seketika ke kernel OS tanpa disimpan ke disk atau database.
    * 100% On-Premise Tanpa Cloud Perantara: Berjalan murni di jaringan lokal atau kabel USB offline tanpa server pihak ketiga dan bebas pelacak telemetri.
    * Proteksi Akses Fisik PIN 6-Digit: Hanya perangkat yang memasukkan PIN di layar PC fisik yang dapat mengontrol, diperkuat mitigasi brute-force bertingkat.
    * Isolasi Endpoint Localhost: Endpoint eksekusi prompt dan PIN tertutup rapat dari akses jaringan luar.

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
2. DigiSmartDeck kini menggunakan SATU metode tunggal untuk dikte suara: **Google Web Speech API**.
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
- Klien komersial (pembeli APK Android) tidak perlu menyetel port di `chrome://flags` karena aplikasi Android resmi (`DigiSmartDeck.apk`) menggunakan WebView dengan izin mikrofon internal native.
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

---

## 8. CATATAN CHECKPOINT (v0.9.4 - AI Workstation Finalized, Centered Deck, & Refined OS Logos)
- **AI Workstation Siap Produksi (Finalized):**
  - Tata letak prompt deck, tuts enter besar, kontrol audio/mic, dan tombol transkripsi telah matang dan ergonomis.
  - Mode siap untuk proses finishing komersial.
- **Menu Deck Mengambang Rata Tengah (Center Modal):**
  - Pop-up Menu Deck (`#control-deck`) kini rata tengah sempurna (vertikal & horizontal) dengan border keliling 16px dan backdrop blur elegan. Tampilan proporsional di tablet maupun ponsel pintar tanpa ruang kosong menganga.
  - Bagian "Pilih Mode Kerja" di dalam menu telah dihapus karena sudah tersedia sebagai pintasan ghost icon di header bar atas.
- **Scanner Multi-Kanal Pemulihan Koneksi Otomatis:**
  - Modal reconnecting beroperasi 100% otomatis tanpa tombol manual membingungkan, memindai seluruh kanal (Wi-Fi LAN, Kabel USB, Bluetooth, Scan QR) dengan animasi radar pulse elegan.
- **Kejernihan Garis Logo OS di Pengaturan:**
  - Logo target sistem operasi (Windows, Apple, dan Linux Tux) disetel dengan ketebalan garis tipis (`stroke-width: 0.5px`) sehingga kontur, tekstur, dan bentuk khasnya tajam dan mudah dikenali.

---

## 9. CATATAN CHECKPOINT (v0.9.5 - Real-Time Trackpad Editor & Keyboard Settings Persistence)
- **Editor Trackpad Real-Time (Mode Keyboard Utama):**
  - Trackpad utama kini dilengkapi tombol roda gigi (*borderless ghost gear icon*) di sudut kanan atas tanpa kotak latar dan tanpa perubahan warna, berputar 60 derajat saat diklik.
  - Overlay editor real-time berada tepat di tengah area trackpad dengan layout 2 baris yang lega:
    - Baris 1: Togel tersegmentasi status trackpad (`Trackpad: [On | Off]`) dan posisi (`Posisi: [Atas | Bawah]`).
    - Baris 2: Slider pengatur tinggi trackpad secara real-time (`Tinggi: [persentase] [slider]`).
  - Seluruh setelan tersimpan otomatis di `localStorage` tanpa tombol simpan manual.
  - Mengklik kembali tombol roda gigi langsung menutup overlay editor secara instan.
  - Tampilan permukaan trackpad dipercantik dengan watermark halus "Trackpad" di bagian tengah menggantikan teks panduan lama.
- **Penyimpanan Pengaturan Keyboard Otomatis (Settings Persistence):**
  - Status toggle panel keyboard utama (Tombol FN, Tombol Navigasi, Numpad, dan Bar Pintasan) kini tersimpan permanen di `localStorage`.
  - Mode yang aktif tidak kembali ke default saat halaman dimuat ulang atau saat berpindah antar mode kerja.
- **Penyempurnaan Ergonomi AI Workstation:**
  - Latar belakang kolom AI Workstation dibuat transparan dengan jarak antar kolom proporsional (8px).
  - Jarak vertikal tombol mikrofon diselaraskan seimbang: jarak ke batas bar atas sama dengan jarak ke batas kotak transkrip (~38px).
  - Lebar badge AI WORKSTATION di kolom kiri dibuat 100% sejajar dengan tombol di atasnya.
- **Sistem Hapus Multi-Tier Backspace (Tap-and-Hold):**
  - 1x tap & tahan: menghapus karakter per karakter (interval 60ms).
  - 2x tap & tahan: menghapus per kata (interval 140ms).
  - 3x tap & tahan: menghapus per 5 kata (interval 240ms).
  - Ketukan instan tanpa tahan menghapus 1 karakter (1x), 1 kata (2x), atau 5 kata (3x).

---

## 10. CATATAN CHECKPOINT (v0.9.6 - Dynamic Shift Layer & Signature 5-Tuts Startup Jingle)
- **Transformasi Layer Shift Dinamis (Keyboard Utama):**
  - Saat tombol Shift aktif, seluruh karakter alternatif pada keyboard utama tampil secara eksklusif (hanya karakter alternatif saja yang aktif), persis seperti metode pergantian huruf besar dan huruf kecil.
  - Tombol angka (1-0) dan simbol tanda baca menyembunyikan elemen sub-label (`display: none`) dan menampilkan karakter alternatif (`!`, `@`, `#`, `~`, `{`, `:`, `<`, `?`, dsb.) secara penuh dan rata tengah.
  - Tombol navigasi panah menyembunyikan simbol panah dan menampilkan teks navigasi alternatif (`PgUp`, `Home`, `PgDn`, `End`) tebal dan berwarna aksen.
  - Melepas Shift langsung mengembalikan seluruh tombol ke tampilan karakter dasar dan sub-label secara mulus.
- **Jingle Ketukan Mekanikal 5-Tuts pada Splash Screen (Flash Screen):**
  - Memanfaatkan suara ketukan mekanikal asli keyboard utama (`playClickSound()`) dengan resonansi sasis bodi yang tergrounding mantap (`bodyPitch = 1 + (pitch - 1) * 0.35`).
  - Ritme 5-tuts mengetik alami manusia:
    - Note 1 dan 2: masing-masing setengah ketukan (ketukan ganda cepat, 0ms dan 90ms).
    - Jeda 1 ketukan (180ms).
    - Note 3: satu ketukan (270ms).
    - Istirahat 1 ketukan (durasi + istirahat 360ms).
    - Note 4 dan 5: sama-sama satu ketukan (630ms dan 810ms).
  - Komposisi nada bergantian natural layaknya jari tangan kiri dan kanan (`0.94 -> 1.08 -> 0.98 -> 1.14 -> 1.28`), secara sengaja berakhir di nada tinggi yang renyah dan positif untuk membangkitkan semangat dan menaikkan energi psikologis pengguna saat hendak mulai bekerja.
  - Durasi splash screen disetel optimal ke 1050ms agar nada penutup berdering sempurna sebelum transisi fade-out ke aplikasi.

---

## 11. CATATAN CHECKPOINT (v0.9.7 - Mode Media Controller, Mode Canvas Tablet, & Penyesuaian Ruang Lingkup)
- **Penyesuaian Ruang Lingkup (Scope Reduction):**
  - Rencana Mode Game Wheel Steer (setir mobil balap gyroscope) resmi ditiadakan dari roadmap karena terlalu kompleks dan di luar batasan esensial proyek.
- **Mode Media Controller (`#media-view`):**
  - Remote pengendali multimedia dan hiburan PC dari sofa atau ranjang.
  - Tombol aksi utama: Hero Play/Pause besar bergradien elegan dengan visualizer equalizer animasi responsif saat musik/video berputar.
  - Kontrol navigasi playback: Prev Track, Mundur 10s (`-10s`), Play/Pause, Maju 10s (`+10s`), Next Track, Stop, Fullscreen (`F`), Subtitle (`CC`), dan pengatur kecepatan putar.
  - Profil Preset Aplikasi Cerdas:
    - *Global Media Keys*: Menggunakan scancode hardware universal kernel Linux (`uinput`) & `pynput` fallback (`KEY_PLAYPAUSE`, `KEY_NEXTSONG`, `KEY_PREVIOUSSONG`, `KEY_VOLUMEUP`, `KEY_VOLUMEDOWN`, `KEY_MUTE`, `KEY_STOPCD`).
    - *YouTube / Web Browser*: Pintasan Space, J/L (seek 10s), Shift+P/N, F, C, dan percepat/perlambat.
    - *Spotify Desktop*: Pintasan Ctrl+Panah (Next/Prev), Shift+Panah (Seek), Space.
    - *VLC Media Player*: Pintasan Space, Ctrl+Panah (Seek 10s), N/P, V (Subtitle), [/] (Kecepatan).
    - *Netflix / Streaming*: Pintasan Space, Panah Kiri/Kanan, F, M.
  - Master Volume Slider PC real-time (0 - 100%) dengan sinkronisasi `pactl`/`amixer` di backend, step tombol volume (+/- 5%), tombol Mute instan, dan pil preset cepat (0%, 25%, 50%, 75%, 100%).
  - D-Pad arah navigasi (Up, Down, Left, Right, OK) untuk kemudahan browsing menu streaming.
- **Mode Canvas Tablet (`#canvas-view`):**
  - Mengubah layar sentuh HP atau tablet menjadi drawing tablet & digitizer pad untuk melukis, mencoret dokumen, atau membuat sketsa.
  - Kanvas HTML5 resolusi tinggi Retina/HiDPI (`window.devicePixelRatio`) dengan garis halus anti-aliased.
  - Pilihan perkakas: Pena Halus (Pen), Spidol/Highlighter Semi-Transparan (Marker), dan Penghapus (Eraser).
  - Pilihan ukuran goresan presisi: 2px (Tipis), 5px (Sedang), 12px (Tebal), 24px (Marker).
  - Palet warna esensial: Biru Aksen, Putih, Hijau, Merah, Kuning, Ungu.
  - Sinkronisasi Kursor PC Real-Time (`mouseabs`, `mousedown`, `mouseup`):
    - Coretan di ponsel dapat langsung memandu kuas mouse di aplikasi PC seperti Photoshop, Figma, Krita, MS Paint, Whiteboard, atau OneNote.
    - Sakelar toggle cepat "Kursor PC: [On | Off]" untuk memilih mode menggambar lokal mandiri atau mirroring ke PC.
    - Fitur Undo bertingkat (riwayat kanvas lokal + otomatis mengirim Ctrl+Z ke PC) dan tombol Bersihkan.
- **Integrasi Pintasan Header Bar:**
  - Ikon ghost mode baru `quick-mode-media` dan `quick-mode-canvas` terpasang di bar atas.
  - Dukungan parameter URL otomatis: `?mode=media` dan `?mode=canvas`.

---

## 12. CATATAN CHECKPOINT (v0.9.8 - Penyederhanaan Tampilan untuk MVP)
- **Fokus Tunggal pada 3 Mode Utama MVP:**
  - Demi menjaga kesederhanaan, kematangan, dan stabilitas peluncuran produk pertama (Minimum Viable Product):
    1. Keyboard PC Utama (`quick-mode-standard`)
    2. Game Console (`quick-mode-game`)
    3. AI Workstation (`quick-mode-ai`)
- **Penyembunyian Mode Sekunder dari Antarmuka (Preserved for Future):**
  - Tiga mode tambahan (Mode Slide Presentasi, Mode Media Controller, dan Mode Canvas Tablet) disembunyikan dari toolbar header (`display: none`).
  - Seluruh kode arsitektur backend Python (`server.py`), scancode evdev/pynput, simulasi absolut kursor (`mouseabs`), pengaturan volume, dan modul tampilan frontend tetap utuh dan tersimpan rapi, sehingga siap diaktifkan kembali pada pembaruan versi mendatang tanpa perlu menulis ulang dari awal.

---

## 13. CATATAN CHECKPOINT (v0.9.9 - Pemisahan Perilaku Tombol Panah AI Workstation)
- **Tombol Panah Kolom Kanan (`#ai-nav-pad` di bawah tombol Enter):**
  - Dikhususkan eksklusif hanya untuk navigasi langsung ke PC (`send({ type: 'keypress', key: 'up'/'down'/'left'/'right' })`).
  - Tidak terpengaruh sama sekali oleh status toggle target ketik (`aiKbTarget` / HP vs PC). Kapan pun tombol panah di bawah Enter ditekan, kursor dan riwayat di PC selalu berpindah.
  - Mempertahankan fitur tap dan tahan repeat interval dengan efek audio mekanikal `playClickSound()` dan getaran `vibe()`.
- **Tombol Panah Keyboard Ketik AI (`#ai-tk-btn-*` pada row 4 keyboard bawah):**
  - Tetap terikat dengan toggle target ketik (`aiKbTarget`), sehingga dapat menggeser kursor teks transkrip di HP (`moveAiCursor*()`) saat mode Device aktif, atau mengirim ke PC saat mode PC aktif.

---

## 14. CATATAN CHECKPOINT (v0.9.10 - Optimasi Alur Auto-Kirim Tanpa Duplikasi)
- **Visual Feedback Tetap Aktif di Layar HP:**
  - Saat Auto-Kirim (`aiAutoSend`) aktif, teks ucapan dan ketikan tetap tampil di kotak teks preview ponsel (`#ai-transcript-preview`). Pengguna tetap dapat melihat kata-kata yang diucapkan secara real-time tanpa merasa buta di HP.
- **Pencegahan Duplikasi Teks (Zero Double Entry):**
  - Kata-kata yang diucapkan atau diketik dialirkan secara streaming langsung ke PC (`sendAiText`).
  - Saat tombol `ENTER` raksasa (`#ai-btn-enter`) ditekan dengan Auto-Kirim aktif:
    1. Teks tidak dikirim ulang ke PC (karena sudah terkirim saat bicara/ketik).
    2. Kotak teks di ponsel langsung dibersihkan (`clearTranscriptUI()`).
    3. Perintah `Enter` langsung dikirim ke PC untuk mengeksekusi prompt/perintah terminal secara instan.
  - Saat tombol `Kirim ke PC` (`#btn-ai-tr-send`) ditekan dengan Auto-Kirim aktif:
    - Kotak teks dibersihkan tanpa mengirim ulang teks, menghindari tumpukan duplikat.
- **Sinkronisasi Presisi State Auto-Kirim:**
  - Mengetik huruf (`handleCharInput`), menghapus huruf (`doDeleteChar`), menghapus kata (`doDeleteWord`/`doDelete5Words`), dan tombol Delete (`ai-btn-delete`) otomatis menyinkronkan `lastSentLength` saat Auto-Kirim aktif.
  - Mengaktifkan sakelar Auto-Kirim otomatis menyinkronkan batas `lastSentLength` ke panjang teks saat ini.

---

## 15. CATATAN CHECKPOINT (v0.9.11 - Optimasi Tombol Shortcut Prompt Dua Baris & Padding)
- **Format Dua Baris untuk Tombol 1 Kolom (`.ai-prompt-chip:not(.span-2)`):**
  - Tombol pintasan prompt yang berukuran 1 kolom dan memiliki 2 kata (misal: "Perbaiki Bug", "Buat Dokumen", atau kustomisasi lainnya) otomatis dipecah menjadi 2 baris terpisah (`<br>`) agar teks tampil rapi, proporsional, dan mudah dibaca.
  - Jika pengguna memasukkan lebih dari 2 kata pada slot 1 kolom, teks otomatis dibagi seimbang menjadi 2 baris.
  - Slot ke-5 (`span-2`) tetap berukuran lebar 2 kolom dan menampilkan teks dalam 1 baris penuh.
- **Pemberian Padding & Tipografi Aman:**
  - Menambahkan `padding: 2px 4px;` dan `box-sizing: border-box;` pada `.ai-prompt-chip` sehingga huruf tidak lagi mepet ke pinggir atau garis tepi tombol.
  - Mengatur `line-height: 1.12;` dan `word-break: break-word;` agar kedua baris teks berada tepat di tengah tombol secara vertikal dan horizontal.

---

## 16. CATATAN CHECKPOINT (v0.9.12 - Penguncian Mode Melintang Landscape & Guard Potret)
- **Penguncian Orientasi Landscape pada Web App & PWA:**
  - File `manifest.json` diperbarui dari `"orientation": "any"` menjadi `"orientation": "landscape"` sehingga saat diinstal via Chrome (Add to Home screen / WebAPK), aplikasi secara otomatis terkunci pada mode horizontal di level sistem operasi.
  - File proyek native Android (`AndroidManifest.xml`) tetap terjaga dengan `android:screenOrientation="sensorLandscape"`.
  - Integrasi JavaScript Screen Orientation API (`screen.orientation.lock('landscape')`) dieksekusi otomatis pada gestur pertama, saat memasuki layar penuh (`toggleFullscreen`), maupun saat menekan tombol pengunci.
- **Proteksi Tampilan Potret (Orientation Landscape Guard):**
  - Mencegah kekacauan tata letak saat perangkat dibuka dalam posisi vertikal (potret).
  - Ditambahkan elemen `#orientation-landscape-guard` yang otomatis muncul saat `@media screen and (orientation: portrait)` dengan kartu panduan dan tombol instan `Kunci Mode Melintang (Landscape)`.
  - Media query `.ai-main-grid` dipertahankan tetap 3 kolom (`120px 1fr 130px`) sehingga tata letak deck tidak pernah roboh menjadi 1 kolom bertumpuk ke bawah.

---

## 17. CATATAN CHECKPOINT (v0.9.13 - Standardisasi Label Tombol Keyboard Utama)
- **Penyesuaian Teks & Ikon Tombol Fungsi Utama:**
  - `Tab`: Menggunakan teks murni `Tab` (ikon panah `⇥` dihilangkan).
  - `Caps`: Menggunakan teks murni `Caps` (ikon panah `⇪` dihilangkan).
  - `Enter`: Menggunakan teks murni `Enter` (ikon panah `↵` dihilangkan).
  - `Shift` (Kiri & Kanan): Menggunakan teks murni `Shift` (ikon panah `⇧` dihilangkan).
  - `Backspace`: Menggunakan ikon murni `⌫` (teks `Back` dihilangkan).
- Seluruh tombol lainnya (Ctrl, Win, Alt, Space, Arrows, Esc, Fn, Nav) dipertahankan sesuai konfigurasi awal tanpa perubahan.

---

## 18. CATATAN CHECKPOINT (v0.9.14 - Pembersihan Elemen Redundan UI)
- **Tombol Fullscreen di Menu Control Deck (`#btn-fs`):**
  - Disembunyikan (`display: none`) untuk merapikan menu pop-up control deck.
- **Kartu Scan QR pada Pop-up Reconnecting (`#reconnect-banner`):**
  - Kartu "Scan QR" beserta ikonnya dihapus dari dialog pencarian koneksi PC saat terputus.
  - Grid kanal koneksi (`.rc-channels-grid`) disesuaikan menjadi 3 kolom seimbang (`Wi-Fi LAN`, `Kabel USB`, `Bluetooth`).
- **Tombol Keyboard di Gamepad View (`#btn-exit-game`):**
  - Disembunyikan (`display: none`) karena perpindahan mode sudah tersedia secara terpusat di bar navigasi atas.

---

## 19. CATATAN CHECKPOINT (v0.9.15 - Refinement Gamepad: Spacing, Emblem Tengah, Skala Tablet & Simbol Asli PS1)
- **Jarak Proporsional Shoulder Bar (`.gp-shoulders-row`):**
  - Ditambahkan `margin-top: 8px;` pada baris tombol bahu (L1, L2, R1, R2) sehingga tidak lagi menempel rapat dengan top utility bar gamepad.
- **Emblem Gamepad Menggantikan Teks Tengah:**
  - Teks "DIGI GAMEPAD" dan badge dihilangkan untuk tampilan yang bersih dan profesional.
  - Digantikan dengan emblem ikon gamepad minimalis (`.gp-center-emblem`) dengan posisi tengah yang nyaman (`margin-top: 14px`) tanpa kesan berdesakan.
- **Pemanfaatan Ruang Layar Tablet / Layar Lebar (Ergonomic Scaling):**
  - Ditambahkan aturan responsif khusus `@media (min-width: 768px) and (min-height: 480px)`.
  - Area kontrol D-Pad dan Action Diamond diperbesar dari 160px menjadi 210px x 210px.
  - Tombol aksi diperbesar menjadi 64px x 64px (font 22px) dan tombol bahu menjadi tinggi 48px dengan lebar minimum 96px, memanfaatkan ruang kosong secara ergonomis untuk genggaman dua tangan pada tablet.
- **Simbol Otentik PlayStation 1 (PSX Preset):**
  - Menghilangkan teks simbol buatan sendiri dan mengadopsi standar originalitas Sony PlayStation:
    - Atas (X): Segitiga Hijau (`#00e676`)
    - Kanan (A): Lingkaran Merah (`#ff1744`)
    - Bawah (B): Silang Biru (`#2979ff`)
    - Kiri (Y): Kotak Pink (`#ff4081`)
  - Simbol dirender menggunakan vektor SVG geometris presisi tinggi (`.ps-symbol`) dengan filter drop shadow warna menyala (*glow*) dan latar tombol bernuansa konsol retro (`#272c36`).

---

## 20. CATATAN CHECKPOINT (v0.9.16 - Layout Gamepad Vertikal, Penguncian PS1 & Bar Bawah Bersih)
- **Susunan Vertikal Tombol Bahu (L1/L2 dan R1/R2):**
  - Mengubah orientasi baris bahu menjadi kolom vertikal bertumpuk di masing-masing sisi:
    - Sisi Kiri: L1 di atas, L2 di bawah.
    - Sisi Kanan: R1 di atas, R2 di bawah.
  - Bentuk kurva tombol disesuaikan secara ergonomis (L1/R1 membulat di sisi atas, L2/R2 membulat di sisi bawah).
- **Pemindahan Utility Bar ke Bagian Bawah (`.gp-bottom-bar`):**
  - Baris kontrol dipindahkan dari atas layar ke posisi paling bawah agar area permainan dan tombol kontrol atas lebih leluasa dan alami bagi jempol dan jari telunjuk.
- **Restorasi Emblem + Teks Gamepad di Bar Bawah:**
  - Emblem ikon gamepad beserta teks "GAMEPAD" dikembalikan ke sisi kiri baris utilitas bawah (`.gp-badge`).
  - Bagian tengah kontroler (`.gp-deck-center`) dibersihkan dari emblem tengah sehingga hanya menyisakan tombol SELECT dan START yang bersih (*clean*).
- **Penguncian Permanen Pemetaan PlayStation 1 (PSX):**
  - Dropdown pemilihan preset emulator dihapus dari antarmuka pengguna.
  - Gamepad dikunci secara eksklusif menggunakan profil PS1 (PSX) dengan simbol autentik (Segitiga, Lingkaran, Silang, Kotak).

---

## 21. CATATAN CHECKPOINT (v0.9.17 - Gamepad Minimalis: Emblem Tengah Atas, Jarak Ekstra Shoulder & Kontrol Terpusat)
- **Pelebaran Jarak Antar-Tombol Bahu (L1/L2 dan R1/R2):**
  - Jarak pemisah vertikal (`gap`) antara L1 dan L2 serta R1 dan R2 ditingkatkan secara signifikan menjadi 16px (20px pada mode tablet) untuk mencegah salah pencet saat dimainkan di ponsel.
- **Pembersihan Bar Gamepad dan Opsi Analog Stick:**
  - Bar utilitas bawah (`.gp-bottom-bar`) dan pengalih D-Pad/Stick dihapus sepenuhnya.
  - Mengeliminasi elemen `#gp-stick-container` sehingga antarmuka 100% fokus pada directional pad murni bergaya retro PS1.
- **Penempatan Emblem Gamepad di Tengah Atas (`.gp-top-emblem`):**
  - Emblem ikon gamepad beserta teks "GAMEPAD" ditempatkan di tengah atas dengan jarak proporsional dan elegan dari bar atas aplikasi.
- **Pusat Gravitasi Kontroler Terpusat (Centered Controls Group):**
  - Seluruh grup tombol dibungkus ke dalam wadah fleksibel terpusat (`.gp-controls-group`) dengan `justify-content: center` sehingga tata letak gamepad seimbang sempurna di tengah layar tanpa rongga canggung.

---

## 22. CATATAN CHECKPOINT (v0.9.18 - Gamepad Deck Rata-Tengah & Penyesuaian Ruang Estetis)
- **Rata-Tengah Tombol Kontrol Utama (D-Pad, Select/Start, Action Diamond):**
  - Seluruh tombol selain tombol bahu (L1, L2, R1, R2) ditempatkan ke dalam `.gp-main-deck` yang otomatis rata-tengah (`align-items: center; justify-content: space-between;`) di tengah area layar.
- **Penyatuan Baris Atas Bahu & Emblem (`.gp-top-row`):**
  - Tombol bahu (L1/L2 di kiri dan R1/R2 di kanan) kini sejajar di baris atas bersama emblem gamepad di tengahnya.
  - Diberikan jarak proporsional dari bar atas aplikasi (`margin-top: 14px; padding-top: 10px;`) sehingga tidak lagi mepet dan terlihat bersih serta lapang.
- **Pemanfaatan Ruang Layar (Skala Tombol Diperbesar):**
  - Ukuran D-Pad dan Action Diamond diperbesar dari 170px menjadi 184px (mode ponsel) dan 230px (mode tablet) dengan tombol aksi 56px (tablet 70px) untuk mengisi ruang kosong yang sebelumnya terlalu renggang.

---

## 23. CATATAN CHECKPOINT (v0.9.19 - Stik Analog Default, Sound Feedback, Icon Gear Pengaturan & Penyelarasan Rata Tengah)
- **Stik Analog Sebagai Kontrol Arah Default:**
  - D-Pad retro digantikan dengan Stik Analog sebagai kontrol arah bawaan aktif dengan ukuran proporsional (wadah 170px, base 150px, thumb 68px).
- **Efek Suara Klik Mekanikal Konsisten pada Arah & Tombol:**
  - `sendGpKeyDown` kini memanggil `playClickSound(true)` sehingga bunyi klik mekanikal dan respon haptik (`vibe(18)`) selalu keluar saat stik digerakkan atau tombol ditekan.
  - `unlockAudio()` dipanggil pada `touchstart` stik, D-Pad, dan gamepad view untuk memastikan audio browser tidak teredam.
- **Tombol Ikon Gear Pengaturan di Kanan Bawah (`.gp-gear-btn`):**
  - Ikon gear ditempatkan di pojok kanan bawah gamepad dengan animasi putar 60 derajat saat diklik (identik dengan trackpad gear).
  - Membuka overlay pengaturan (`#gamepad-settings-overlay`) yang berisi tombol alih "Stik Analog" vs "Arah Panah" dan tombol konfigurasi pemetaan ("Atur Mapping...").
- **Penyelarasan Sejajar Rata-Tengah Horizontal & Naik ke Posisi Tengah Layar:**
  - Baris bahu atas (`.gp-top-row`) menggunakan pemosisian absolut di bagian atas sehingga `.gp-main-deck` memanfaatkan penuh ruang layar.
  - Seluruh kontrol utama (Stik Analog di kiri, Select & Start di tengah, dan 4 tombol aksi PS1 di kanan) berada pada garis tengah horizontal yang sejajar sempurna dan naik ke posisi tengah layar yang seimbang dan ergonomis.
  - Ukuran elemen tombol tetap dipertahankan sesuai skala asli yang sudah nyaman bagi pengguna.

---

## 24. CATATAN CHECKPOINT (v0.9.20 - Skala Lebih Besar, Pemisahan Bahu Anti-Double-Click, Emblem Kiri Bawah L2 & Audio Arah Instan)
- **Pembesaran Skala Stik & Tombol Aksi:**
  - Stik Analog diperbesar ke ukuran ergonomis: wadah 196px, base 174px, thumb 76px, dan radius jelajah `maxRadius = 52px`.
  - Action Diamond diperbesar ke 196px dengan 4 tombol aksi PS1 (Segitiga, Bulat, Silang, Kotak) berdiameter 62px dan simbol SVG 30px untuk akurasi sentuhan tinggi.
- **Pemindahan Emblem Gamepad ke Sisi Kiri Bawah L1/L2:**
  - Emblem ikon gamepad ditempatkan secara teratur di bawah tombol L2 pada kolom kiri bahu, membebaskan ruang horizontal atas sepenuhnya.
- **Pemisahan Jarak Bahu Proporsional (Anti-Double-Click):**
  - Tombol L1/L2 dan R1/R2 diberi pemisah berjarak proporsional (`gap: 16px`, ukuran tombol 88px x 38px) sehingga jari dapat menekan tombol secara terpisah tanpa risiko memencet dua tombol sekaligus.
- **Audio Feedback Arah & Stik Real-Time:**
  - Memperbaiki inisialisasi dan penjadwalan `AudioContext` serta menambahkan pemicuan klik mekanikal instan pada `touchstart`/`mousedown` pertama stik dan D-Pad.
  - Setiap perubahan arah gerak (Atas, Bawah, Kiri, Kanan) otomatis memicu bunyi klik mekanikal dan getaran haptik.
  - Menambahkan dukungan event mouse/pointer penuh untuk D-Pad dan Stik Analog agar pengujian di peramban desktop berjalan mulus.

---

## 25. CATATAN CHECKPOINT (v0.9.21 - Relokasi Emblem Gamepad & Stik Analog Hening/Silent)
- **Relokasi Emblem Gamepad (.gp-bottom-emblem):**
  - Emblem gamepad dipindahkan dari kolom bahu kiri ke posisi tengah bawah (bottom center) gamepad view.
  - Diposisikan secara presisi tepat di tengah-tengah ruang antara tombol SELECT / START dan batas bawah (border bawah) tampilan gamepad (`top: calc(75% + 10px); left: 50%; transform: translate(-50%, -50%);`).
  - Kolom bahu kiri kini bersih dan simetris dengan kolom bahu kanan, hanya memuat tombol L1 dan L2 tanpa gangguan visual.
  - Penataan gaya responsif otomatis menyesuaikan pada mode lanskap ponsel (`@media (max-height: 480px)`) maupun mode tablet (`@media (min-width: 768px)`).
- **Penonaktifan Suara Klik pada Stik Analog & D-Pad (Silent & Smooth):**
  - Efek suara klik mekanikal dan getaran pada pergerakan arah stik analog dan D-pad dinonaktifkan sepenuhnya (`sendGpKeyDown(pcKey, true)`).
  - Stik analog kini bergerak halus dan hening tanpa bunyi klik berulang saat diarahkan ke berbagai sudut.
  - Efek suara klik mekanikal (`playClickSound()`) tetap dipertahankan penuh pada seluruh tombol aksi lainnya (L1, L2, R1, R2, Segitiga, Lingkaran, Silang, Kotak, Select, dan Start).

---

## 26. CATATAN CHECKPOINT (v0.9.22 - Standarisasi Terminologi Standar Industri & Dukungan Antarmuka Dua Bahasa EN / ID)
- **Standarisasi Seluruh Teks Antarmuka ke Standar Industri:**
  - Menggantikan salinan informal, kasual, atau sisa prompt buatan AI dengan terminologi teknis profesional standar industri periferal emulasi nirkabel.
  - Mencakup top navigation bar, floating control deck, modal rekoneksi jaringan/IP discovery, editor trackpad real-time, dialog pengaturan & remap gamepad, workstation dikte audio AI, modal pengaturan sistem & tema, modal toko produk, serta modal tentang aplikasi.
- **Dukungan Dua Bahasa Lengkap (English & Bahasa Indonesia):**
  - Bahasa default awal disetel ke English (`en`) untuk kenyamanan standardisasi internasional, dengan dukungan penuh terjemahan Bahasa Indonesia (`id`).
  - Kamus terjemahan `I18N` terpasang di client-side JavaScript dengan mekanisme update reaktif berbasis atribut `data-i18n`, `data-i18n-title`, dan `data-i18n-placeholder`.
- **Mode Penggantian Bahasa Interaktif di Menu & Pengaturan:**
  - Tombol alih bahasa interaktif terpasang di Menu Floating Control Deck (Seksi 1) dan di dalam modal Pengaturan (`#settings-modal`).
  - Preferensi bahasa disimpan secara persisten di `localStorage` (`digi_ui_lang`).
  - Preset pintasan prompt AI otomatis menyesuaikan antara varian bahasa Inggris (`Continue`, `Proceed`, `Fix Bug`, `Generate Docs`, `Create Checkpoint`) dan varian bahasa Indonesia saat bahasa antarmuka diganti.
- **Kepatuhan Aturan Mutlak Repositori:**
  - Nol emoji / zero emoticons di seluruh kode, log terminal, antarmuka, dan teks asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan umpan balik getar (`vibe()`) selalu dipertahankan pada seluruh tombol alih bahasa dan elemen dialog.

---

## 27. CATATAN CHECKPOINT (v0.9.23 - Fitur Cerdas 1: Smart App-Context Auto-Switching PC)
- **Deteksi Jendela Aktif PC Host Secara Real-Time (X11 / Windows):**
  - Backend `server.py` menjalankan loop asinkron non-blocking (`smart_context_tracker_loop`) setiap 800ms menggunakan `asyncio.to_thread`.
  - Mengambil parameter sesi X11 (`DISPLAY` dan `XAUTHORITY`) secara otomatis dari `/proc` saat server berjalan di bawah systemd daemon.
  - Menginspeksi `_NET_ACTIVE_WINDOW`, `WM_CLASS`, dan `_NET_WM_NAME` via `xprop` secara efisien (<30ms, CPU <0.1%).
- **Klasifikasi Cerdas Mode Kerja Berdasarkan Aplikasi PC:**
  - `ai` (AI Workstation Mode): Terminal (`gnome-terminal`, `alacritty`, `kitty`, `konsole`, dll.), Editor Kode (`VS Code`, `Cursor`, `Windsurf`, `PyCharm`, `IntelliJ`, `Sublime`, `Neovim`), serta web interface AI (`ChatGPT`, `Claude`, `DeepSeek`).
  - `present` (Presentation Mode): `Impress`, `PowerPoint`, `Keynote`, PDF viewer (`Evince`, `Okular`), Google Slides, Canva.
  - `media` (Media Controller Mode): `VLC`, `Spotify`, `MPV`, `Celluloid`, `YouTube`, `Netflix`.
  - `game` (Gamepad Mode): `Steam`, `RetroArch`, `PCSX2`, `Dolphin`, emulator, dan game runtime.
  - `canvas` (Drawing Mode): `GIMP`, `Krita`, `Inkscape`, `Photoshop`, `Blender`.
  - `standard` (PC Keyboard Mode): Desktop background, file manager, peramban web umum, dan aplikasi lainnya.
- **Penyiar Konteks via WebSocket (`app_context`):**
  - Setiap perubahan jendela aktif atau mode yang disarankan langsung disiarkan ke semua client yang terhubung (`type: "app_context"`).
  - Client yang baru terhubung langsung menerima konteks aplikasi aktif saat inisialisasi handshake WebSocket.
- **Antarmuka Klien Cerdas (Badge Header, Floating Deck & Toast HUD):**
  - Header atas dilengkapi chip interaktif `#smart-context-chip` yang menampilkan nama aplikasi aktif di PC host secara live.
  - Tombol 'Smart Switch' (`#btn-toggle-smart-context`) digabungkan secara rapi ke dalam seksi 'SYSTEM & UTILITIES' (`.deck-chips-utils`) di Floating Control Deck berdampingan dengan Trackpad dan Mod Lock.
  - Modal Pengaturan (`#settings-modal`) dilengkapi opsi dedicated 'Smart App-Context Auto-Switching' dengan tombol alih 'Enabled' (`#btn-st-smart-on`) dan 'Disabled' (`#btn-st-smart-off`) untuk konfigurasi preferensi pengguna yang jelas dan mudah diakses.
  - Seluruh status indikator tersinkronisasi dua arah secara real-time antara badge header, menu deck, dan modal pengaturan.
  - Notifikasi HUD toast muncul halus saat mode berpindah otomatis untuk memberi tahu pengguna perpindahan mode kerja.
  - Menghormati aturan mutlak: nol emoji di seluruh kode/UI/log, efek suara mekanikal (`playClickSound()`) dan haptic feedback (`vibe()`) selalu aktif.

---

## 28. CATATAN CHECKPOINT (v0.9.24 - Simplifikasi UI/UX Pengaturan & Placeholder AI Workstation)
- **Penghapusan Bahasa dari Menu Deck:**
  - Pilihan bahasa tampilan dihapus dari Floating Control Deck (`#control-deck`), kini dikonsolidasikan secara terpusat dan bersih di dalam Modal Pengaturan (`#settings-modal`).
- **Simplifikasi Judul & Label Pengaturan (1-2 Kata Kunci):**
  - Mengubah seluruh judul grup pengaturan menjadi ringkas, profesional, to the point, dan bebas kalimat bertele-tele:
    - 'Bahasa' (Language)
    - 'Sistem Operasi' (Operating System)
    - 'Tema' (Theme)
    - 'Tipografi' (Typography)
    - 'Keyboard' (Keyboard)
    - 'Trackpad' (Trackpad)
    - 'Penguncian Tombol' (Modifier Lock)
    - 'Auto Switch' (Auto Switch)
    - 'Getaran & Audio' (Haptic & Audio)
  - Tombol aksi dan opsi disederhanakan:
    - 'Uji Getaran' (Test Vibration)
    - 'Suara Mekanikal' (Mechanical Sound)
    - 'Uji Suara' (Test Audio)
  - Menghapus teks deskripsi panjang dan notice banner yang tidak perlu (`haptic-device-notice`, `st_sound_notice`, subteks Auto Switch).
- **Simplifikasi Placeholder AI Workstation:**
  - Menggantikan placeholder teks yang panjang dan kaku menjadi frasa singkat dan elegan:
    - Bahasa Indonesia: 'Bicara untuk mendikte...'
    - English: 'Speak to dictate...'
  - Tersinkronisasi dinamis melalui fungsi `clearTranscriptUI()` dan `renderTranscriptPreview()` berbasis kamus I18N.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji di seluruh kode, antarmuka, kamus terjemahan, dan log.
  - Efek suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) tetap aktif sempurna.

---

## 29. CATATAN CHECKPOINT (v0.9.25 - Mekanisme Dinamis Status Mic AI, Ikon Standar USB, & Penyatuan Bahasa 100%)
- **Mekanisme Teks Dinamis Berganti pada Mic AI Workstation (Single-Pass, Tanpa Looping):**
  - Status teks di bawah tombol mikrofon berganti secara elegan satu kali (transisi halus `opacity` & `translateY` 0.28s) tanpa berulang/looping:
    - Saat Mendengarkan: Fase 1 "Mendengarkan..." (tampil 1.6s) -> memudar -> Fase 2 "Ketuk untuk berhenti" (menetap).
    - Saat Teks Tersimpan: Fase 1 "Teks tersimpan" (tampil 1.6s) -> memudar -> Fase 2 "Ketuk Mic untuk lanjut bicara" (menetap).
    - Saat Siap/Idle: Fase 1 "Siap Mendikte" (tampil 1.6s) -> memudar -> Fase 2 "Ketuk Mic untuk bicara" (menetap).
  - Menghapus penimpaan teks status lama di `recognition.onresult` ("Mendengar: ..." dan "Mendengarkan... (Ketuk untuk Berhenti)") sehingga saat berbicara teks status tetap konsisten, bersih, dan tidak terdistorsi.
  - Tombol mic berdenyut halus (*breathing animation*) saat sesi perekaman suara aktif.
- **Ikon Standar Industri USB:**
  - Mengganti ikon rantai (*chain/link*) pada kartu channel rekoneksi dengan simbol standar industri USB trident SVG yang presisi.
- **Penyatuan Bahasa 100% Konsisten (ID / EN):**
  - Seluruh teks yang sebelumnya tercampur atau hardcoded telah diintegrasikan dengan kamus `I18N`:
    - Kartu tema: Native OS / Sesuai OS, Dark Modern, Retro 90s, Cyberpunk, Stealth, Nord Arctic.
    - Tipografi: Bawaan Tema / System Default, Sistem UI / System UI.
    - Ukuran keyboard & trackpad: Kecil / Compact, Normal / Normal, Besar / Large, Ekstra / Extra.
    - Posisi dock trackpad: Dock Atas / Top Docked, Dock Bawah / Bottom Docked.
    - Penguncian tombol: Aktif Terus / Sticky, Kunci 1x / 1-Shot, Tahan Manual / Hold.
    - Preset getaran & volume audio: Lembut, Normal, Kuat / Pelan, Sedang, Keras.
    - Chip deck utilitas: Toko / Store, Getaran / Haptics, Suara Tuts / Key Sound.
    - Dialog peringatan dan konfirmasi (USB Cable switch, Bluetooth HID guide, Web Vibration notice, PWA install prompt) sepenuhnya bilingual sesuai preferensi bahasa aktif.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan UI.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 30. CATATAN CHECKPOINT (v0.9.26 - Indikator Aplikasi Aktif Tengah Bar, Soft Green Dot Glow, & Lokalisasi Total Kunci Modifier)
- **Penempatan Tengah Bar untuk Indikator Aplikasi Aktif PC:**
  - Memindahkan chip aplikasi aktif (`#smart-context-chip`) dari `.left-controls` ke wadah khusus `.center-controls` yang diposisikan secara absolut tepat di tengah bar (`position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);`).
  - Dilengkapi kontrol responsif (`max-width: calc(100% - 240px);` dan `display: none` pada layar super sempit di bawah 380px) agar tidak bertabrakan dengan kontrol sisi kiri maupun tombol mode sisi kanan.
- **Pendaran Halus Titik Hijau Indikator (Anti-Flicker):**
  - Mengimplementasikan animasi pendaran halus (`@keyframes sc-dot-glow`) pada titik hijau aktif (`.smart-context-chip:not(.paused) .sc-dot`):
    - Siklus sinusoidal 2.4s `ease-in-out` bernapas lembut (*breathing glow*).
    - Memancarkan cahaya hijau dengan `box-shadow` bertingkat (dari 4px/8px hingga 8px/18px) dan pembesaran halus (`scale(1)` ke `scale(1.18)`).
    - Menghindari flicker atau kedipan kasar dengan variasi `opacity` terbatas (0.85 hingga 1.0).
- **Lokalisasi Bahasa Indonesia untuk Menu Kunci Modifier (Shift, Ctrl, Alt):**
  - Mengeliminasi teks bahasa Inggris tersisa ("Hold", "1-Shot", "Sticky") saat berpindah mode di Floating Control Deck maupun Modal Pengaturan:
    - Mode Lock: Tombol menampilkan "Aktif Terus" (ID) / "Sticky" (EN).
    - Mode One-Shot: Tombol menampilkan "Kunci 1x" (ID) / "1-Shot" (EN).
    - Mode Hold: Tombol menampilkan "Tahan" (ID) / "Hold" (EN).
  - Memperbarui tooltip dan deskripsi panduan di modal pengaturan dengan penyebutan tombol modifier `(Shift, Ctrl, Alt)` secara eksplisit dan konsisten.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan UI.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 31. CATATAN CHECKPOINT (v0.9.27 - Tipografi King Ali Studiō & Proteksi Mutlak Bebas Pop-up Saat Flash Screen)
- **Tipografi King Ali Studiō (Huruf o dengan Garis Atas / Macron):**
  - Mengubah penulisan nama studio menjadi "King Ali Studiō" dengan karakter 'ō' (U+014D):
    - Subtitle layar pembuka / flash screen (`.splash-sub`): "by King Ali Studiō".
    - Header atas tombol branding (`#btn-brand-toggle`): tooltip title "About DigiSmartDeck - King Ali Studiō" (EN) / "Tentang DigiSmartDeck - King Ali Studiō" (ID).
    - Modal Tentang / Informasi Aplikasi (`#modal-about`): subtitle pahlawan "by King Ali Studiō".
    - Kamus terjemahan `I18N.en` dan `I18N.id` untuk entri `brand_title`.
- **Proteksi Mutlak Bebas Pop-up Saat Flash Screen (Splash Screen):**
  - Memastikan antarmuka bersih tanpa gangguan pop-up, modal, banner, atau toast apa pun selama layar pembuka (flash screen 1050ms) aktif:
    - Lapisan CSS Guard: Menambahkan aturan selektor `body:has(#splash-screen:not(.fade-out))` yang secara eksplisit menyembunyikan `.orientation-guard`, `.reconnect-banner`, `.smart-context-toast`, dan seluruh `.modal-backdrop` dengan `display: none !important;`.
    - Level z-index: Menaikkan `z-index` `.splash-screen` menjadi `100000000 !important;` agar selalu menempati lapisan teratas tanpa potensi tembus pandang atau bleed-through.
    - Lapisan JavaScript Guard: Menambahkan state `isSplashScreenActive = true` yang memblokir pemanggilan fungsi `showSmartContextToast()`, `showReconnectBanner()`, `openReconnectModal()`, dan `openAboutModal()` sampai flash screen selesai dan terhapus dari DOM.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan antarmuka.
  - Suara klik mekanikal (`playClickSound()`) dan efek jingle ketikan startup tetap aktif sempurna.

---

## 32. CATATAN CHECKPOINT (v0.9.28 - Simplifikasi Label Target Kontrol & Penyatuan Cluster Toggle PC/Device)
- **Simplifikasi Label Target Kontrol ("Target:"):**
  - Menggantikan judul panjang "Target Kontrol Keyboard: Host PC atau Input Lokal" menjadi frasa ringkas satu kata "Target:".
  - Diperbarui secara konsisten di kamus terjemahan `I18N.en` dan `I18N.id` (`ai_target_label: "Target:"`).
  - Label tombol diselaraskan menjadi "PC" dan "Device".
- **Penyatuan Cluster Elemen Target Dekat Toggle PC/Device (Khusus Keyboard):**
  - Menghilangkan jarak renggang `space-between` yang memisahkan teks label dan tombol toggle:
    - Wadah `.ai-tk-control-bar` kini menggunakan perataan rapi `justify-content: flex-end`.
    - Dibuatkan kontainer khusus `.ai-tk-target-cluster` dengan `display: inline-flex; align-items: center; gap: 5px;` sehingga label "Target:" dan tombol toggle `[PC] [Device]` berdampingan langsung di atas baris tuts keyboard tablet.
  - Sektor mikrofon / header transkripsi dikte suara (`.ai-transcript-header`) tetap bersih dan fokus pada pemilihan bahasa (`ID` / `EN`), karena pengiriman teks suara telah ditangani secara mandiri dan intuitif oleh fitur Auto-Kirim serta tombol Kirim ke PC.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan UI.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 33. CATATAN CHECKPOINT (v0.9.29 - Eliminasi Total Duplikasi & Pengulangan Transkrip Mic AI)
- **Akar Masalah Duplikasi Transkrip Google STT di Mobile (Android/Chrome):**
  - Peramban Chrome dan WebView di Android sering mengirimkan potongan transkripsi secara kumulatif atau ganda di dalam event `SpeechRecognition.onresult`, di mana item `event.results[i]` dapat memuat ulang seluruh kalimat sebelumnya atau mengulang frasa yang baru saja diucapkan.
  - Sebelumnya, potongan transkrip digabungkan menggunakan spasi biasa (`join(' ')`) dan fungsi `mergeTranscripts` tidak pernah dipanggil di dalam siklus streaming `onresult` maupun `commitCurrentSession`. Hal ini menyebabkan teks berlipat ganda berkali-kali baik di layar ponsel maupun saat terkirim ke PC host via Auto-Kirim.
- **Penyatuan Cerdas Berbasis `mergeTranscripts` Real-Time:**
  - `recognition.onresult` kini menyatukan seluruh potongan final (`finalPieces`) dan interim (`interimPieces`) menggunakan `mergeTranscripts(merged, piece)`.
  - Teks sesi aktif (`currentSessionText`) disatukan dari gabungan final dan interim tanpa menghasilkan duplikat kalimat yang sedang diucapkan.
  - Teks preview live (`liveText`) menggabungkan teks tersimpan (`aiAccumulatedText`) dengan sesi aktif secara cerdas tanpa pengulangan buffer lama.
  - Fungsi `commitCurrentSession()` menggabungkan teks final ke `aiAccumulatedText` via `mergeTranscripts`, mencegah penumpukan teks identik antar-sesi dikte.
  - Alur Auto-Kirim (`aiAutoSend`) menggunakan `mergeTranscripts(aiAccumulatedText, currentSessionFinal)` dengan pelindung batas panjang (`lastSentLength`), memastikan hanya kata baru murni yang diketikkan ke PC host.
- **Optimasi Pembersih Frasa & Tumpang Tindih Kata (`deduplicateRepeatedPhrases` & `mergeTranscripts`):**
  - Mengizinkan deteksi pengulangan kata tunggal untuk teks pendek (ambang batas diturunkan dari `< 3` menjadi `< 2`), sehingga pengulangan 2 kata seperti "halo halo" atau "buka buka" langsung dibersihkan.
  - Mendukung eliminasi tumpang tindih 1 kata pada batas sambungan (`len === 1`), mencegah pengulangan kata di perbatasan chunk ucapan.
  - Mempertahankan kata ulang sah dalam Bahasa Indonesia (`commonIndoDuplication`: 'hati-hati', 'pelan-pelan', 'sama-sama', 'pagi-pagi', dsb.).
  - Normalisasi kata bersih berbasis Unicode huruf/angka (`\p{L}\p{N}`) sehingga tanda baca bawaan Google STT tidak merusak proses pencocokan awalan/akhiran.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan UI.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 34. CATATAN CHECKPOINT (v0.9.30 - PC Window Switcher & Task Manager Dropdown dari Header Bar)
- **Menu Dropdown Jendela PC pada Indikator Header Bar (`#smart-context-chip`):**
  - Chip indikator aplikasi aktif PC di tengah header bar kini dilengkapi ikon panah dropdown (`.sc-chevron`).
  - Mengklik chip akan membuka pop-up modal "Aplikasi Terbuka di PC" (`#modal-window-switcher`) yang menampilkan seluruh daftar aplikasi/jendela GUI yang sedang berjalan di PC host.
- **Backend Task Inspector & Window Manager (`server.py`):**
  - Fungsi `get_open_windows_list()`: Memindai daftar jendela aktif menggunakan `wmctrl -l -x` (Linux) dan `win32gui` (Windows), mengecualikan window desktop wallpaper/dock `-1`, serta memetakan kelas jendela ke nama ramah (`app`) dan mode rekomendasi (`suggested_mode`).
  - Fungsi `activate_and_focus_window(win_id, maximize=True)`: Mengangkat jendela pilihan ke latar depan (`wmctrl -i -a <id>`) dan memaksimalkan ukurannya ke jendela penuh (`wmctrl -i -r <id> -b add,maximized_vert,maximized_horz`).
  - Penanganan pesan WebSocket `get_window_list` dan `activate_window` yang secara langsung menyiarkan status aplikasi aktif terbaru ke seluruh client.
- **Antarmuka Interaktif Pengalihan Jendela & Otomatisasi Mode:**
  - Setiap item jendela dalam daftar menampilkan ikon kategori mode (Terminal/AI, Media, Game, Kanvas, Keyboard), nama aplikasi, badge "Aktif" untuk jendela yang sedang fokus, judul jendela, serta tag mode kerja.
  - Mengetuk jendela pilihan akan memicu bunyi klik mekanikal (`playClickSound()`), getaran haptik (`vibe(20)`), menutup popover, mengirim perintah aktivasi & pemaksimalan ke PC, serta langsung mengubah mode DigiSmartDeck di ponsel agar sesuai dengan aplikasi tersebut (misal Terminal/VS Code langsung masuk ke AI Workstation).
  - Dilengkapi tombol Segarkan (`#btn-refresh-win-switcher`) untuk memperbarui daftar jendela secara real-time.
- **Dukungan Dua Bahasa Lengkap (ID / EN):**
  - Entri kamus terjemahan `win_switcher_*` terpasang penuh di `I18N.id` dan `I18N.en`.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan antarmuka.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 35. CATATAN CHECKPOINT (v0.9.31 - Tema Solid: Racing, Anime, Sakura, Pastel Cantik, Pelangi Warna & RGB Lampu Jalan)
- **Eliminasi Total Background Gambar & Wallpaper Overlays demi Keterbacaan Maksimal:**
  - Sesuai arahan pengguna, seluruh lapisan gambar background, wallpaper SVG, dan fitur unggah foto kustom dari galeri dihapus total.
  - Tampilan kembali bersih, ringan, dan fokus pada warna solid harmonis tanpa ada distorsi kontras di tuts maupun area kerja AI.
- **Koleksi Tema Warna Solid Baru:**
  - `theme-racing` (Racing Supercar): Sasis obsidian pekat, panel serat karbon, aksen merah Rosso Corsa (`#ff3b30`) dengan garis bawah tuts merah balap.
  - `theme-anime` (Anime Mecha): Biru ruang angkasa tengah malam, panel mecha navy, aksen cyber cyan menyala (`#00e5ff`) dan garis bawah tuts cyan.
  - `theme-sakura` (Sakura Floral): Nuansa plum anggun dengan aksen cherry blossom pink (`#ff80bf`) yang feminin dan lembut.
  - `theme-pastel` (Pastel Cantik): Palet pastel estetis feminin berlatar dark-lavender (`#1b1622`) dengan aksen rose pastel (`#f8c8dc`) dan warna pastel per baris tuts (peach `#ffb7b2`, melon `#ffdac1`, pistachio `#e2f0cb`, mint `#b5ead7`, periwinkle `#c7ceea`).
  - `theme-rainbow` (Pelangi Warna): Palet spektrum pelangi cerah berlatar midnight obsidian dengan aksen multi-warna di tiap baris tuts (merah `#ff595e`, oranye `#ff924c`, kuning `#ffca3a`, hijau `#8ac926`, biru `#1982c4`).
  - `theme-rgb-wave` (RGB Lampu Jalan): Efek pencahayaan Chroma RGB neon dinamis dengan animasi berjalan halus (`rgb-running-light 4s linear infinite`) pada garis pemisah header bar dan border tuts keyboard.
- **Perbaikan Total Kontras AI Workstation:**
  - Menghapus layer wallpaper fixed yang sebelumnya menutupi tombol-tombol AI Workstation karena perbedaan stacking context CSS.
  - Tombol-tombol pintasan cepat AI (`.ai-prompt-chip`), tombol tool (`.ai-btn-sh`), tuts QWERTY, tombol panah navigasi, dan tombol Enter kini memiliki kontras tinggi dengan teks putih solid (`#ffffff`), border kiri aksen warna tema (`border-left: 3px solid var(--accent)`), dan bayangan tegas.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan antarmuka.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) aktif pada pemilihan seluruh tema dan tombol interaktif.

---

## 36. CATATAN CHECKPOINT (v0.9.32 - Penonaktifan Menu Toko / Store & Tema Rainbow Multicolor Cerah Ceria)
- **Penonaktifan (Mute) Menu Toko / Store:**
  - Tombol Store (`#btn-store`) pada Control Deck disembunyikan (`display: none;`) dan fungsinya dinonaktifkan sepenuhnya.
  - Pemanggilan fungsi `openStore()` dikunci dengan early return sehingga modal store tidak dapat terbuka.
- **Penyederhanaan Nama Tema Rainbow:**
  - Label tema diubah dari sebelumnya "Vibrant Rainbow" (EN) / "Pelangi Warna" (ID) menjadi ringkas: `Rainbow` di seluruh kamus i18n dan antarmuka pemilih tema.
- **Desain Multicolor Penuh Cerah Ceria pada Tema Rainbow:**
  - Seluruh tuts keyboard pada tema Rainbow kini menggunakan latar belakang warna gradien spektrum pelangi cerah ceria dengan kontras tajam:
    - Baris 1 (Angka): Gradien merah coral stroberi (`#ff2a5f` -> `#d81141`) dengan border pink.
    - Baris 2 (QWERTY): Gradien oranye jingga matahari (`#ff7a00` -> `#e65c00`) dengan border oranye terang.
    - Baris 3 (Home Row): Gradien hijau zamrud segar (`#00c853` -> `#009624`) dengan tombol Enter hot magenta fuchsia (`#ff007f`).
    - Baris 4 (ZXCV): Gradien biru langit elektrik (`#00b0ff` -> `#0077c2`).
    - Baris 5 (Bawah/Modifier): Gradien ungu royal violet (`#9c27b0` -> `#6a0080`), spasi multicolor pelangi (`linear-gradient(90deg, #ff2a5f, #ff7a00, #00c853, #00b0ff, #9c27b0)`), serta tombol panah navigasi kuning emas cerah (`#ffd600`).
  - AI Workstation mengadopsi palet senada pada tombol pintasan cepat, tuts QWERTY, tombol enter, trackpad, dan ring mikrofon.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan antarmuka.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 37. CATATAN CHECKPOINT (v0.9.33 - Harmonisasi Warna Tombol Enter, Kirim ke PC & Efek Mic Listening Sesuai Tema)
- **Harmonisasi Warna Tombol Enter & Kirim ke PC (`Send to Host`):**
  - Tombol Enter raksasa AI Workstation (`.ai-btn-giant-enter`) dan tombol Kirim ke PC (`#btn-ai-tr-send` / `.ai-btn-tr-act.primary`) tidak lagi dikunci dengan warna hijau statis.
  - Keduanya kini dinamis mengikuti variabel tema aktif (`var(--enter-bg)` dan `var(--enter-border)`):
    - Tema Racing: Merah sasis balap Rosso Corsa pekat (`#b71c1c` / `#ff3b30`).
    - Tema Anime: Mecha navy cyber dengan aksen border cyan menyala (`#7b1fa2` / `#00e5ff`).
    - Tema Sakura: Plum blossom anggun dengan border cherry blossom pink (`#ad1457` / `#ff80bf`).
    - Tema Pastel: Mauve feminin lembut dengan border rose pastel (`#85587a` / `#f8c8dc`).
    - Tema Rainbow: Hot magenta fuchsia cerah ceria (`#ff007f` / `#ff66b2`).
    - Tema RGB Wave: Neon violet bercahaya dengan border cyan (`#7700ff` / `#00f0ff`).
    - Tema Dark / OS Default: GitHub blue modern (`#1f6feb` / `#388bfd`).
- **Efek Mic Listening & Label Status Selaras Tema:**
  - Animasi pendaran denyut mic (`.ai-btn-mic.recording` via `@keyframes ai-pulse-theme`) kini memancarkan gelombang ripple lingkaran dengan warna aksen tema aktif (`var(--accent)`), bukan warna hijau statis lagi.
  - Khusus tema RGB Lampu Jalan (`theme-rgb-wave`), pendaran denyut mic menggunakan animasi spektrum RGB neon multi-warna (`@keyframes rgb-mic-pulse`).
  - Label status teks dikte ("Mendengarkan...", "Teks tersimpan") di bawah tombol mic otomatis diwarnai sesuai warna aksen tema aktif.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan antarmuka.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 38. CATATAN CHECKPOINT (v0.9.34 - Penghapusan Tema Rainbow & RGB)
- **Penghapusan Bersih Tema Rainbow & RGB:**
  - Seluruh aturan CSS untuk `theme-rainbow` dan `theme-rgb-wave` (termasuk animasi `@keyframes rgb-running-light` dan `@keyframes rgb-mic-pulse`) dihapus sepenuhnya dari stylesheet.
  - Kartu pemilih tema `Rainbow` dan `RGB Chroma Wave` dihapus dari modal Pengaturan (`#settings-modal`).
  - Pratinjau `.tp-rainbow` dan `.tp-rgb-wave` dihapus dari CSS.
  - Entri teks terjemahan `theme_rainbow` dan `theme_rgb_wave` dihapus dari kamus `I18N.en` dan `I18N.id`.
- **Daftar Tema Aktif yang Dipertahankan:**
  - `os-native`, `dark`, `retro`, `cyberpunk`, `stealth`, `nord`, `racing`, `anime`, `sakura`, `pastel`.
- **Proteksi Fallback Aman pada `applyTheme`:**
  - Menambahkan array `VALID_THEMES`. Jika browser client memiliki sisa riwayat tema `rainbow` atau `rgb-wave` di `localStorage`, sistem otomatis melakukan fallback aman ke `os-native` tanpa menyebabkan kerusakan tampilan.
- **Kepatuhan Aturan Mutlak:**
  - Nol emoji / emotikon di seluruh berkas dan antarmuka.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 39. CATATAN CHECKPOINT (v0.9.35 - Device Pairing Otentikasi 6-Digit PIN & Sistem SaaS Licensing)
- **Percabangan Git Baru:**
  - Dibuat percabangan `feature/pairing-and-auth` dari `test/concept-a-deck`.
- **Modul Keamanan & Lisensi Mandiri (`auth_manager.py`):**
  - `DevicePairingManager`:
    - Mengenerate 6 digit PIN acak yang dicetak di terminal host PC saat server mulai/restart.
    - Memverifikasi PIN perangkat mobile saat pertama kali tersambung dan menerbitkan token otentikasi permanen 48-char hex (`data/paired_devices.json`).
    - Otomatis mem-bypass localhost/koneksi kabel internal (127.0.0.1, ::1).
    - Mendukung unpairing / pencabutan otorisasi perangkat dari daftar.
  - `LicenseManager`:
    - Mengelola model bisnis SaaS: Free Trial 7 Hari (otomatis aktif saat instalasi baru), Paket Bulanan (Rp 15.000 / bulan), dan Paket Seumur Hidup (Rp 250.000).
    - Menggunakan verifikasi tanda tangan digital HMAC-SHA256 untuk aktivasi lisensi offline/online tanpa ketergantungan server luar (`DIGI-MONT-XXXX-XXXX`, `DIGI-LIFE-XXXX-XXXX`).
    - Status tersimpan persisten di `data/license.json`.
- **Integrasi Server Host (`server.py`):**
  - Banner startup menampilkan PIN Pairing 6-digit dan status lisensi SaaS secara transparan.
  - Endpoint REST: `GET /api/license`, `GET /api/pairing/pin`.
  - Protokol WebSocket: Penjagaan pesan (`keypress`, `text`, `mouse`, `action`, dll.). Klien yang belum ter-pairing dibatasi dan diminta memasukkan PIN.
  - Penanganan pesan WS baru: `auth`, `pair_request`, `get_pairing_info`, `unpair_device`, `activate_license`.
- **Antarmuka Klien Mobile & Deck (`static/index.html`):**
  - Modal Otorisasi Pairing Baru (`#modal-pairing`) dengan 6 kotak input PIN angka otomatis melompat (auto-jump / backspace handler).
  - Modal Lisensi & Akun SaaS (`#modal-license`) menampilkan status aktif, sisa hari aktif, paket harga berlangganan (Rp 15.000/bln & Rp 250.000), serta input aktivasi lisensi.
  - Tombol akses cepat status lisensi (`#btn-license`) dan pairing (`#btn-pairing`) di Control Deck.
  - Dukungan dwibahasa penuh (EN & ID) di kamus `I18N`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant responses.
  - Mechanical click sound (`playClickSound()`) and haptics (`vibe()`) preserved on all new UI buttons.

---

## 40. CATATAN CHECKPOINT (v0.9.36 - Aplikasi Desktop PC Host Control GUI & Pintasan Linux)
- **Aplikasi Desktop PC Host Manager (`digikeyboard_gui.py`):**
  - Dibangun aplikasi desktop native menggunakan PyQt5 untuk PC host (Linux/Ubuntu/X11).
  - Tampilan modern bertema gelap selaras dengan branding DigiSmartDeck.
  - Fitur Pusat Kendali Desktop:
    - Status Server Real-time: Badge indikator aktif di port 8080.
    - PIN Pairing 6-Digit: Ditampilkan besar dan jelas dengan tombol salin dan acak ulang PIN.
    - Alamat Koneksi & QR Code: Menampilkan IP Wi-Fi fisik lokal (`192.168.8.x`) serta QR Code presisi tinggi (`Pillow` + `io.BytesIO`) yang siap discan kamera ponsel.
    - Manajemen Perangkat Terhubung: Tabel daftar perangkat yang sudah ter-pairing dengan tombol putuskan/unpair.
    - Manajemen Lisensi SaaS: Status paket aktif (Trial, Monthly, Lifetime), sisa hari, dan dialog aktivasi lisensi.
    - Aksi Cepat: Tombol "Buka DigiSmartDeck di Browser" (`xdg-open`) dan "Restart Layanan Server".
- **Ikon Aplikasi & Pintasan Desktop Linux:**
  - Ikon aplikasi resmi dibuat: `assets/icon.png` dan `static/icon.png`.
  - File Desktop Entry dibuat di `~/.local/share/applications/digikeyboard.desktop` (muncul di menu aplikasi sistem operasi) dan `~/Desktop/digikeyboard.desktop` (pintasan desktop langsung).
  - CLI symlink: `~/.local/bin/digikeyboard` sehingga aplikasi dapat dipanggil dari terminal mana saja.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant responses.
  - APK client Android tetap ringan (~20 MB).

---

## 41. CATATAN CHECKPOINT (v0.9.37 - Sinkronisasi PIN Multi-Proses & Auto-Connect Otomatis Tanpa Tekan Tombol)
- **Sinkronisasi Shared PIN Antara Server & Desktop GUI:**
  - Masalah teridentifikasi: `server.py` dan `digikeyboard_gui.py` berjalan sebagai proses terpisah. Sebelumnya PIN hanya tersimpan di memori instance masing-masing sehingga PIN yang ditampilkan di GUI berbeda dengan yang diverifikasi server.
  - Solusi: `DevicePairingManager` di `auth_manager.py` kini menyimpan `current_pin` dan `pin_created_at` secara terpusat di `data/paired_devices.json`.
  - GUI desktop memprioritaskan pengambilan PIN langsung dari endpoint REST `http://127.0.0.1:8080/api/pairing/pin` sehingga nilai PIN di GUI, terminal, dan server selalu 100% identik.
- **Otomasi Pairing Instan (Zero-Click Auto-Connect):**
  - Pada antarmuka client mobile (`static/index.html`), begitu digit ke-6 selesai dimasukkan atau dipaste:
    - Permintaan pairing (`pair_request`) langsung dikirim seketika melalui WebSocket tanpa mengharuskan pengguna menekan tombol "Sambungkan".
    - Tombol manual "Sambungkan" disembunyikan dan digantikan teks panduan otomatis.
    - Begitu verifikasi server sukses (`pairing_result.success: true`), token langsung tersimpan di `localStorage`, modal pairing otomatis menutup, kelas `controller-standby` dilepas ("otomatis on"), dan keyboard langsung aktif digunakan dengan feedback haptik dan audio mekanikal.
    - Jika PIN salah, 6 kotak input otomatis dikosongkan dan kursor otomatis kembali fokus ke kotak pertama untuk memudahkan pengetikan ulang.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant responses.
  - Suara klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 42. CATATAN CHECKPOINT (v0.9.38 - Validasi Sukses: Zero-Click Device Pairing & Otorisasi Dua Perangkat Android)
- **Status Pengujian Lapangan:**
  - Telah diverifikasi pengujian langsung dari perangkat fisik Android.
  - Otorisasi perangkat berhasil penuh dengan dua ponsel Android aktif terdaftar di `data/paired_devices.json`:
    - Perangkat 1: IP `192.168.8.103` (terotentikasi dan terdaftar pukul 12:47:56).
    - Perangkat 2: IP `192.168.8.102` (terotentikasi dan terdaftar pukul 12:49:47).
- **Hasil Alur Zero-Click Auto-Connect:**
  - Pengguna memasukkan 6 digit PIN langsung di antarmuka mobile.
  - Otorisasi terhubung otomatis tanpa menekan tombol "Sambungkan" manual.
  - Antarmuka keyboard dan AI Workstation langsung aktif seketika ("otomatis on").
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant responses.
  - Audio klik mekanikal dan haptik responsif berjalan normal.

---

## 43. CATATAN CHECKPOINT (v0.9.39 - Desain Ulang Terpadu Aplikasi PC Host & Installer Selaras Web Client)
- **Desain Ulang Menyeluruh PC Host Manager (`digikeyboard_gui.py`):**
  - Palet warna dan hierarki visual diselaraskan 100% dengan Web Client (`#0d1117` background obsidian navy, `#161b22` header & nav bar, `#1c2128` card panels, `#ff6b00` aksen oranye brand, `#3fb950` status online, `#58a6ff` cyber blue).
  - Top Deck Bar: Menampilkan logo `DIGISMARTDECK HOST`, badge status pulsa real-time, chip indikator latensi (<1ms), dan tombol pintas `Buka Web Client`.
  - Navigasi Deck Chips:
    - Tab 1 (Pusat Kendali): Tampilan 6-Digit PIN bergaya tombol keycap mekanikal individual terpisah (`[ 6 ] [ 6 ] [ 7 ] [ 2 ] [ 3 ] [ 0 ]`), modul QR code scanner beresolusi tinggi, dan panduan metode koneksi (Wi-Fi vs kabel USB tethering).
    - Tab 2 (Perangkat Terdaftar): Tabel daftar perangkat terotorisasi dengan opsi putuskan koneksi per-perangkat atau putuskan semua.
    - Tab 3 (Lisensi SaaS): Kartu status paket aktif, 3 kartu pilihan paket komersial (Trial Rp 0, Bulanan Rp 15.000, Lifetime Pro Rp 250.000), serta form aktivasi kunci lisensi.
    - Tab 4 (Wizard Setup & Layanan): Pengecekan status izin kernel hardware (`/dev/uinput`), status layanan background (`digikeyboard.service`), kontrol restart layanan, dan penampil log aktivitas server real-time (`journalctl`).
- **Pembaruan Skrip Installer Linux (`install-linux.sh`):**
  - CLI installer diharmonisasikan dengan identitas visual DigiSmartDeck.
  - Otomatis mendaftarkan dependensi PyQt5 & Pillow, memasang pintasan desktop, dan meluncurkan antarmuka GUI Host Manager setelah instalasi.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant responses.
  - Audio klik mekanikal dan haptik responsif dipertahankan.

---

## 44. CATATAN CHECKPOINT (v0.9.40 - Pembersihan Efek Garis Berwarna di Tombol Shortcut Mode AI)
- **Pembersihan Garis Aksen Berwarna pada Shortcut AI:**
  - Menghilangkan `border-left: 3px solid var(--accent);` pada `.ai-btn-sh.ai-prompt-chip` di `static/index.html`.
  - Seluruh tombol pintasan di deck AI Workstation (`.ai-btn-sh` dan prompt chips) kini memiliki border netral yang seragam dan bersih (`border: 1px solid var(--key-border)`) di semua tema.
  - Tampilan visual tidak lagi terganggu oleh garis aksen vertikal di tepi tombol shortcut AI.
- **Preservasi Desain Garis pada Keyboard Fisik / Virtual:**
  - Desain garis berwarna pada tombol keyboard fisik/virtual (`.k`) pada tema-tema seperti Racing Supercar (`border-bottom: 2px solid #e63946`), Anime Mecha (`border-bottom: 2px solid #00e5ff`), Sakura Floral (`border-bottom: 2px solid #ff80bf`), dan Pastel Chic (`border-top: 2px solid ...`) tetap dipertahankan penuh sesuai permintaan.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant responses.
  - Audio klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`) dipertahankan penuh.

---

## 45. CATATAN CHECKPOINT (v0.9.41 - Perbaikan Tombol Shoulder Gamepad L1, L2, R1, R2)
- **Penyebab Masalah:**
  - Tombol bahu gamepad (L1, L2, R1, R2) berada di dalam container HTML `<div class="gp-top-row">`.
  - Pada event listener multi-touch dan mouse di `#gamepad-view` (`touchstart`, `touchend`, dan `mousedown`), terdapat pengecekan pengabaian: `if (e.target.closest('#gp-dpad, #gp-stick-container, .gp-top-row')) return;`.
  - Akibatnya, setiap sentuhan atau klik pada tombol L1, L2, R1, dan R2 terdeteksi berada di dalam `.gp-top-row` dan langsung dihentikan (`early return`) sebelum sempat memicu fungsi penanganan tombol (`handleButtonTouch` / `mousedown`).
- **Solusi yang Diterapkan:**
  - Menghapus selektor `.gp-top-row` dari daftar pengecualian di event `touchstart`, `touchend`, dan `mousedown` pada `#gamepad-view`.
  - Menambahkan fallback `|| t.target` pada `document.elementFromPoint` di `handleButtonTouch` agar pendeteksian elemen tombol pada perangkat layar sentuh selalu akurat dan andal.
  - Tombol L1, L2, R1, R2 kini dapat diklik dan disentuh normal, merespons dengan audio klik mekanikal (`playClickSound()`), getaran haptik (`vibe()`), dan mengirim sinyal tombol ke PC host via WebSocket.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.

---

## 46. CATATAN CHECKPOINT (v0.9.42 - Kontrol Jendela PC: Tombol Minimize, Maximize, dan Close per Aplikasi)
- **Kontrol Jendela di Daftar Aplikasi Aktif (Modal Window Switcher):**
  - Pada popup daftar aplikasi PC (`modal-window-switcher` yang dibuka via indikator aplikasi aktif `#smart-context-chip`), kini setiap baris aplikasi dilengkapi dengan 3 tombol kontrol jendela interaktif:
    1. **Minimize (`[ - ]`)**: Meminimalkan jendela ke taskbar tanpa menutupnya (menggunakan X11 `XIconifyWindow` dan `wmctrl -b add,hidden` di Linux, serta `ShowWindow(SW_MINIMIZE)` di Windows).
    2. **Maximize / Restore (`[ ▢ ]`)**: Memaksimalkan jendela ke layar penuh atau memulihkan ukuran jendela sebelumnya (`wmctrl -b toggle,maximized_vert,maximized_horz` di Linux, `ShowWindow(SW_MAXIMIZE/SW_RESTORE)` di Windows).
    3. **Close (`[ ✕ ]`)**: Menutup jendela aplikasi secara anggun (`wmctrl -c` di Linux, `WM_CLOSE` di Windows) dengan animasi transisi memudar dan pembaruan otomatis daftar jendela.
  - Mengetuk badan kartu aplikasi tetap berfungsi untuk mengaktifkan/membawa jendela ke depan di PC dan menyesuaikan mode layout DigiSmartDeck.
  - Setiap tombol kontrol jendela dilengkapi isolasi event (`stopPropagation()`), efek suara klik mekanikal (`playClickSound()`), getaran haptik (`vibe()`), dan notifikasi toast status di layar ponsel.
- **Backend & Protokol WebSocket (`server.py`):**
  - Menambahkan endpoint pesan `control_window` (`action`: `minimize`, `maximize`, `close`, `activate`) yang dieksekusi secara asinkron (`asyncio.to_thread`).
  - Setelah aksi jendela dilakukan, server otomatis menyiarkan status konteks aplikasi aktif yang baru (`app_context`) dan daftar jendela terkini (`window_list`) ke seluruh klien yang terhubung secara real-time.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Audio klik mekanikal dan respons haptik dipertahankan penuh.

---

## 47. CATATAN CHECKPOINT (v0.9.43 - Pencegahan Trigger Tidak Disengaja pada Host Manager & Single-Instance Lock)
- **Penyebab Terpicunya Aplikasi Host / Installer (`digikeyboard_gui.py`):**
  1. *Host Manager Muncul di Window Switcher:* Pemindaian jendela di `get_open_windows_list()` sebelumnya tidak menyaring `digikeyboard_gui.py`. Akibatnya, jendela Host Manager muncul di daftar switcher dan ketika disentuh atau tertekan akan mengeksekusi `activate_window` yang mengangkat Host Manager ke layar penuh.
  2. *Event Bubbling pada Kartu Switcher:* Ketukan pada tombol kontrol jendela sebelumnya dapat merambat ke event listener `item` yang memaksa aktivasi layar penuh (`maximize: true`).
  3. *Ketiadaan Single-Instance Lock:* `digikeyboard_gui.py` dapat diluncurkan berkali-kali tanpa batasan, sehingga penekanan shortcut atau aktivasi berulang membuat beberapa jendela host manager terbuka sekaligus.
  4. *Fokus Desktop:* Jika seluruh jendela diminimalkan ke desktop di mana `~/Desktop/digikeyboard.desktop` aktif, penekanan tombol `Enter` dapat mengeksekusi launcher desktop tersebut.
- **Solusi yang Diterapkan:**
  1. *Filter Jendela Internal di `server.py`:* Menyaring dan mengecualikan secara mutlak jendela `digikeyboard`, `digikeyboard_gui`, dan `host manager` dari `get_open_windows_list()` dan `get_active_window_info()`. Host Manager tidak akan pernah muncul di daftar popup dan tidak akan mengacaukan smart context auto-switch.
  2. *Isolasi Event & Aktivasi Tanpa Paksaan di `static/index.html`:*
     - Menambahkan pencegahan perambatan event (`pointerdown`, `touchstart`, `click` di `.win-switcher-controls` dan `pointer-events: none` pada icon SVG).
     - Mengubah aktivasi default kartu menjadi `maximize: false` agar jendela hanya dibawa ke depan sesuai ukuran aslinya.
  3. *Single-Instance Lock di `digikeyboard_gui.py`:* Mengimplementasikan abstract UNIX domain socket lock (`\0digikeyboard_host_gui_lock`). Jika instance GUI sudah berjalan di sistem, proses baru tidak akan membuat jendela duplikat, melainkan mengangkat jendela yang ada atau keluar dengan bersih.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.

---

## 48. CATATAN CHECKPOINT (v0.9.44 - Audio Feedback Canggih & Elegan Saat Pairing PIN Berhasil)
- **Desain Audio Penerimaan Sistem (System Access Granted Chime):**
  - Menggantikan bunyi klik tuts keyboard biasa (`playClickSound()`) pada keberhasilan otorisasi pairing PIN dengan fungsi audio sintetis khusus `playPairingSuccessSound()`.
  - Disintesis murni menggunakan Web Audio API tanpa dependensi file audio eksternal, menjaga ukuran aplikasi tetap ringan (~20 MB Android APK) dan bekerja instan offline.
  - Karakteristik Akustik Canggih & Elegan:
    - *Inisiasi / Anchor Tone*: Frekuensi 587.33 Hz (D5) berdurasi 75ms sebagai nada pemicu.
    - *Fondasi Hangat*: Sub-frekuensi 293.66 Hz (D4) untuk memberikan kedalaman suara pada speaker ponsel pintar.
    - *Resolusi Harmonis Sistem*: Nada 880.00 Hz (A5) berdurasi 200ms dengan decay eksponensial halus, membentuk lompatan interval nada kelima murni yang melambangkan konfirmasi dan otorisasi.
    - *Sheen Kristal Digital*: Overtone segitiga 1760.00 Hz (A6) bervolume rendah untuk memberikan sentuhan futuristik, elegan, dan jernih.
    - *Durasi Ringkas*: Total durasi ~270ms, tidak terlalu panjang dan tidak bertele-tele.
- **Integrasi Event Otorisasi:**
  - Dipicu seketika saat PIN 6-digit berhasil diverifikasi oleh server (`pairing_result.success: true`) dan saat aktivasi lisensi SaaS berhasil (`license_activation_result.success: true`).
  - Dilengkapi haptic pulse `vibe([30, 40])` dan notifikasi toast status di layar.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) pada tuts keyboard dan workstation tetap dipertahankan penuh.

---

## 49. CATATAN CHECKPOINT (v0.9.45 - Desain Ulang Modal Info Aplikasi: Borderless, Bersih & Bahasa Marketing Awam)
- **Pembersihan Total Elemen & Border (Zero Clutter):**
  - Menghilangkan seluruh border pada modal dialog, kartu, header, dan footer (`border: none;`).
  - Menghapus seksi media sosial (YouTube, Instagram, TikTok, Website) dan seksi kontak (WhatsApp, Telepon, Email).
  - Menghapus judul/label "About DigiSmartDeck" dan icon pendukung.
  - Menyediakan tombol tutup '✕' minimalis tanpa border di sudut kanan atas dialog serta penutupan instan saat mengetuk latar belakang (backdrop).
- **Tata Letak Informasi Ringkas 4 Elemen Utama:**
  - *Line 1*: Nama aplikasi `DigiSmartDeck` berbobot tebal dan proporsional.
  - *Line 2*: Badge versi aplikasi `v1.17.0` berbentuk kapsul aksen biru elegan.
  - *Line 3*: Teks studio `by King Ali Studiō` dengan karakter 'ō' beraksen macron yang presisi.
  - *Subtitle*: Deskripsi bahasa awam berorientasi marketing yang ramah pengguna, mudah dipahami, serta menonjolkan fitur unggulan dan kegunaan nyata:
    - ID: "Ubah ponsel atau tablet Anda menjadi keyboard nirkabel, mouse sentuh (trackpad), stik game, dan pengetik suara otomatis untuk laptop atau PC. Kendalikan komputer dengan mudah dan praktis dari genggaman tanpa repot kabel."
    - EN: "Turn your phone or tablet into a wireless keyboard, smooth touch trackpad, game controller, and voice-typing tool for your PC or laptop. Control your computer effortlessly from anywhere without messy cables."
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna.

---

## 50. CATATAN CHECKPOINT (v0.9.46 - Kalimat Ringkas Subtitle & Integrasi Tombol Periksa Pembaruan)
- **Penyederhanaan Subtitle Aplikasi (Kalimat Terakhir Sah):**
  - Mengurangi teks penjelasan info aplikasi menjadi hanya satu kalimat penutup yang padat, ringkas, dan fokus pada manfaat utama:
    - ID: "Kendalikan komputer dengan mudah dan praktis dari genggaman tanpa repot kabel."
    - EN: "Control your computer effortlessly from anywhere without messy cables."
- **Penempatan Tombol Update di Posisi Bawah Tengah (Bottom Center):**
  - Tombol kapsul minimalis `#btn-check-update` diletakkan di bagian paling bawah tengah dialog modal.
  - Sesuai standar industri UI/UX (visual flow dari info ke aksi, serta kemudahan jangkauan ibu jari / thumb zone pada layar sentuh).
  - Dilengkapi ikon putar sinkronisasi SVG dan efek animasi putar halus (`spin-icon 0.8s`).
  - Mengambil data versi dari endpoint `/api/version`, memicu audio penerimaan sistem (`playPairingSuccessSound()`), getaran haptik (`vibe(15)`), dan toast notifikasi status.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) pada tuts keyboard dan workstation tetap dipertahankan penuh.

---

## 51. CATATAN CHECKPOINT (v0.9.47 - Perbaikan Deteksi Terminal di Window List & Konsistensi Audio Mechanical Keyboard)
- **Perbaikan Masalah Jendela Terminal Tidak Muncul di Window List:**
  - *Akar Masalah*: Pada `get_open_windows_list()`, filter aplikasi internal sebelumnya mengecek substring `'digikeyboard' in title.lower()`. Ketika pengguna membuka folder repositori `~/digikeyboard` di terminal, window title terminal otomatis menjadi `nino@Jarvis: ~/digikeyboard`, yang secara keliru ikut tersaring keluar.
  - *Solusi*: Filter diperketat hanya untuk aplikasi Host GUI (`'digikeyboard_gui'` pada `wm_class` atau `'host manager'` / `'DigiSmartDeck Host'` pada window title), sehingga jendela Terminal, VS Code, maupun editor lain yang membuka direktori `digikeyboard` tetap tampil 100% di daftar aplikasi aktif.
- **Konsistensi Audio & Pengalaman Mengetik Mechanical Keyboard:**
  - *Penyebab Suara Tidak Aktif pada Sentuhan/Huruf Pertama*:
    1. Status default `soundEnabled` sebelumnya diuji dengan `=== 'true'`, sehingga pengguna baru yang belum menyetel preferensi memiliki nilai default false (terbisu). Diperbaiki menjadi `!== 'false'` agar audio aktif secara default.
    2. Browser membatasi Web Audio pada status `suspended` sebelum interaksi pengguna. Sebelumnya pemanggilan `resume()` bersifat asinkron sehingga audio pada ketukan pertama terpotong sebelum konteks audio aktif. Kini `playClickSound` secara otomatis meresume dan menjadwalkan suara klik begitu status audio siap (`audioCtx.resume().then(...)`).
    3. Pada AI Workstation, fungsi `bindAiKey` sebelumnya menunda aksi hingga `touchend`. Kini tombol bereaksi seketika pada downstroke (`touchstart`), mengeliminasi jeda sentuh dan membuka kunci audio secara instan.
  - *Peningkatan Akustik Tuts Keyboard Mekanikal (Tactile & Clack)*:
    - Lapisan 1: Transient click tajam (1800Hz -> 380Hz, gelombang segitiga snap switch).
    - Lapisan 2: Resonansi housing bawah tuts (320Hz -> 85Hz, gelombang sinus thock mantap).
    - Lapisan 3: Metallic spring ping (2600Hz -> 900Hz, tekstur per mekanikal renyah).
    - Micro-pitch randomization alami per tuts agar suara ketikan beruntun terdengar organik layaknya keyboard mekanikal fisik asli.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 52. CATATAN CHECKPOINT (v0.9.48 - Tombol Undo Pemulihan Kotak Teks AI Workstation)
- **Tombol Aksi Undo pada Baris Tindakan Kotak Teks (`#btn-ai-tr-undo`):**
  - Ditambahkan tombol `Undo` berdampingan dengan `Clear` dan `Send to Host` di bagian kanan bawah kotak teks dikte AI Workstation.
  - Menyelaraskan alur kerja produktivitas: jika pengguna salah mengirim prompt, mengirim teks yang belum selesai, atau tidak sengaja mengosongkan kotak teks, kondisi teks sebelumnya dapat dipulihkan secara instan tanpa perlu mengetik atau mendikte ulang dari awal.
- **Sistem Riwayat Undo State (`pushAiUndoState` & `undoAiTranscript`):**
  - Menyimpan snapshot teks (`aiAccumulatedText`) dan posisi kursor (`aiCursorPos`) ke dalam stack riwayat (`aiUndoHistory`) hingga 15 entri sebelum kotak dikosongkan (`clearTranscriptUI`).
  - Menekan tombol Undo memulihkan teks dan posisi kursor secara langsung ke pratinjau (`renderTranscriptPreview`).
  - Mengunci `lastSentLength` ke panjang teks yang dipulihkan saat Auto-Send aktif, mencegah teks terkirim ulang secara otomatis ke PC sebelum pengguna selesai menyunting.
  - Memberikan umpan balik suara klik mekanikal (`playClickSound()`), getaran haptik (`vibe(15)`), dan notifikasi toast status.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 53. CATATAN CHECKPOINT (v0.9.49 - Rebranding Penuh DigiSmartDeck & Integrasi Aset Desain Logo Baru)
- **Rebranding Menyeluruh Proyek ke DigiSmartDeck:**
  - Pembaruan nama brand resmi dari `DigiKeyboard` menjadi `DigiSmartDeck` secara konsisten di seluruh kode sumber backend, frontend, dokumen arsitektur, panduan komersial, skrip build/installer, workflow CI/CD GitHub Actions, dan konfigurasi Android.
  - File cache PWA di `sw.js` diperbarui ke `digismartdeck-cache-v1`.
  - Tautan aktivasi SaaS dan jaringan affiliasi diarahkan ke `https://mayar.link/digismartdeck-pro` dan `https://mayar.link/affiliate/digismartdeck`.
- **Integrasi Desain & Generasi Aset Logo Baru (`DigiSmartDeck/`):**
  - Mengonversi aset logo beresolusi tinggi `DigiSmartDeck/Ikon aplikasi@2x.png` (960x960), `Logo utama@2x.png`, dan `Versi gelap@2x.png` ke dalam seluruh ukuran aset produksi:
    - `assets/icon.png`: Ikon utama PC Host (512x512).
    - `assets/logo.png` & `static/logo.png`: Banner horizontal transparent logo (1280x260).
    - `static/icon-512.png`, `static/icon-192.png`, `static/icon.png`: Ikon web dan PWA.
    - `static/icon-maskable.png`: Ikon PWA maskable berlatar navy `#0e1738` dengan padding zona aman native.
    - `static/icon.ico`: Multi-resolusi icon Windows/Favicon (16px hingga 256px).
    - `static/icon.svg`: Vektor SVG resolusi tinggi dengan embedding data baru.
    - Android Mipmap (`ic_launcher.png`): Menghasilkan aset launcher untuk `mipmap-xxxhdpi`, `xxhdpi`, `xhdpi`, `hdpi`, dan `mdpi`.
- **Integrasi Antarmuka UI:**
  - Splash screen awal memuat ikon logo baru DigiSmartDeck.
  - Header top bar menampilkan ikon logo baru di samping teks DigiSmartDeck.
  - Modal About menampilkan badge logo baru, nama DigiSmartDeck, versi, dan tombol update.
  - GUI Host Manager (`digikeyboard_gui.py`) menampilkan logo ikon baru pada header deck atas.
- **Kompilasi APK Android Mandiri:**
  - Berhasil mengompilasi `DigiSmartDeck.apk` (5.4 MB, jauh di bawah batas 20 MB).
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 54. CATATAN CHECKPOINT (v0.9.50 - Perbaikan Izin Runtime Android APK untuk Mikrofon & Bluetooth)
- **Akar Masalah Izin pada Versi APK:**
  - Pada `AndroidManifest.xml` sebelumnya, deklarasi izin `android.permission.RECORD_AUDIO` dan `android.permission.MODIFY_AUDIO_SETTINGS` belum terdaftar. Akibatnya, sistem operasi Android langsung memblokir akses perekaman suara / speech recognition.
  - Pada `MainActivity.java`, implementasi `WebChromeClient` sebelumnya menggunakan implementasi default yang secara otomatis menolak (`request.deny()`) permintaan izin `PermissionRequest` dari WebView untuk audio capture.
  - Belum ada alur permintaan izin runtime (`ActivityCompat.requestPermissions`) saat aplikasi pertama kali dijalankan.
- **Solusi Komprehensif:**
  - Menambahkan deklarasi izin lengkap di `AndroidManifest.xml`:
    - `android.permission.RECORD_AUDIO`
    - `android.permission.MODIFY_AUDIO_SETTINGS`
    - `android.permission.BLUETOOTH_ADVERTISE`
    - Fitur hardware opsional `android.hardware.microphone`.
  - Mengimplementasikan `onPermissionRequest(PermissionRequest request)` di `WebChromeClient` pada `MainActivity.java` untuk secara otomatis memberikan izin audio capture kepada WebView.
  - Menambahkan fungsi `checkAndRequestPermissions()` di `onCreate()` untuk memunculkan dialog persetujuan izin runtime mikrofon dan Bluetooth saat aplikasi pertama kali dibuka.
  - Menambahkan jembatan JavaScript (`DigiAndroidBridge.hasAudioPermission()` dan `DigiAndroidBridge.requestAudioPermission()`) yang memicu dialog izin sistem jika pengguna menekan tombol mic di AI Workstation saat izin belum diberikan.
  - Kompilasi ulang APK mandiri (`DigiSmartDeck.apk`, 5.5 MB) di `dist/` dan `static/` yang dapat langsung diunduh dan dipasang di perangkat HP/tablet.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 55. CATATAN CHECKPOINT (v0.9.51 - Jembatan Native Android SpeechRecognizer & Eliminasi Cache WebView/Service Worker)
- **Penyebab Masalah pada Aplikasi APK yang Terpasang:**
  1. *Limitasi Web Speech API di Android WebView*: Berdasarkan spesifikasi Chromium, API `window.webkitSpeechRecognition` tidak didukung secara native oleh komponen embedded WebView Android (berbeda dengan browser Google Chrome mandiri). Memanggilnya di WebView menyebabkan error silent atau tidak dapat terhubung ke cloud speech service.
  2. *Cache WebView & Service Worker*: WebView secara default (`LOAD_DEFAULT`) membaca cache lokal halaman `index.html` dan Service Worker lama (`v1`). Akibatnya, meskipun server di PC telah diperbarui dengan menu dan fitur baru, layar ponsel tetap menampilkan aset cache versi lama.
- **Solusi Komprehensif:**
  1. *Jembatan Native Android SpeechRecognizer (`android.speech.SpeechRecognizer`)*:
     - Mengimplementasikan `SpeechRecognizer` native langsung di `MainActivity.java`.
     - Menghubungkan event native (`onReadyForSpeech`, `onPartialResults`, `onResults`, `onError`, `onEndOfSpeech`) ke JavaScript WebView melalui `window.onNativeSpeech*`.
     - Mengaktifkan streaming partial recognition langsung ke teks preview AI Workstation dan mekanisme Auto-Send.
  2. *Eliminasi Cache Total (Instant Real-time Update)*:
     - Server backend (`server.py`): Menambahkan header HTTP `Cache-Control: no-cache, no-store, must-revalidate` pada `index_handler`.
     - WebView Client (`MainActivity.java`): Mengatur `settings.setCacheMode(WebSettings.LOAD_NO_CACHE)` dan mengeksekusi `webView.clearCache(true)` saat memuat server.
     - PWA Service Worker (`sw.js`): Meningkatkan versi cache ke `digismartdeck-cache-v2` yang otomatis memusnahkan cache lama saat aktivasi.
  3. *Kompilasi Ulang APK Mandiri*:
     - File APK baru (`DigiSmartDeck.apk`, 5.5 MB) telah dikompilasi dan siap diunduh ulang dari `http://<IP-PC>:8080/static/DigiSmartDeck.apk`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 56. CATATAN CHECKPOINT (v0.9.52 - Otomatisasi Status "Paired" & Notifikasi Eksplisit "Up to Date")
- **Pembaruan Status Pairing ("Paired"):**
  1. *Top-Bar Status Badge*: Saat perangkat HP/klien tersambung dan diotorisasi oleh host PC, label `#badge-txt` otomatis menampilkan teks "Paired" berwarna hijau (#3fb950) di samping ikon koneksi.
  2. *Floating Deck Chip Button*: Label tombol chip pairing (`#deck-pairing-lbl`) otomatis berubah menjadi "Paired" saat tersambung.
  3. *Modal Pairing Dialog*: Jika perangkat sudah berhasil dipasangkan sebelumnya atau sedang terhubung, pembukaan dialog pairing langsung mengonfirmasi status "Status: Perangkat Paired (Terhubung)".
  4. *Notifikasi Sambungan*: Toast konfirmasi menampilkan pesan status "Status: Paired (Perangkat Terhubung)" disertai audio feedback `playPairingSuccessSound()`.
- **Pembaruan Fitur Periksa Pembaruan ("Check for Updates"):**
  1. *Notifikasi Up to Date Jelas & Eksplisit*:
     - Ketika pengguna menekan tombol "Periksa Pembaruan" dan aplikasi telah berada pada versi terkini, sistem menampilkan pesan: "Versi aplikasi Anda sudah yang terbaru (v1.17.0)."
     - Teks pesan ditampilkan langsung di modal About melalui container `#about-update-status`, tombol berubah menjadi "Versi Sudah Terbaru" / "Up to Date", dan smart toast muncul di layar.
     - Diberikan umpan balik suara (`playPairingSuccessSound()`) dan getaran haptik (`vibe(15)`).
- **Sinkronisasi IP Default APK & Rebuild:**
  - `MainActivity.java` dan `strings.xml` disinkronkan ke IP aktif host `192.168.8.102:8080`.
  - APK mandiri (`DigiSmartDeck.apk`, 5.5 MB) telah dikompilasi ulang dan diperbarui di direktori `dist/` dan `static/`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 57. CATATAN CHECKPOINT (v0.9.53 - Eliminasi Clutter Top-Bar & Pemusatan Indikator Paired di Menu Deck)
- **Keputusan Desain & Optimalisasi Tampilan Layar:**
  1. *Top-Bar Bebas Clutter*:
     - Teks "Paired" di samping ikon Wi-Fi dihilangkan sepenuhnya (`display: none`).
     - Badge status kembali ke format asli yang bersih, elegan, dan minimalis: hanya titik status (dot hijau saat aktif) + ikon koneksi + angka latensi ping (ms).
     - Menghemat ruang horizontal pada header sehingga tidak terasa sesak di layar ponsel (mode landscape).
  2. *Pemusatan Status Paired pada Menu Deck*:
     - Informasi pairing dialihkan secara eksklusif ke dalam menu popup Floating Control Deck (`#btn-pairing`).
     - Saat perangkat berhasil terpasang dan tersambung, tombol chip pairing di dalam menu menyala dengan kelas aktif (`.on`) dan menampilkan teks "Paired".
     - Jika perangkat terputus atau membutuhkan otorisasi PIN baru, tombol kembali berlabel "Pairing" normal.
     - Di dalam modal dialog Pairing (`#modal-pairing`), status tetap memberikan konfirmasi visual "Status: Perangkat Paired (Terhubung)".
  3. *Kompilasi Ulang APK*:
     - File APK (`DigiSmartDeck.apk`, 5.5 MB) di `dist/` dan `static/` dikompilasi ulang dan disinkronkan.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 58. CATATAN CHECKPOINT & ROADMAP (v0.9.54 - Roadmap Screen Mirroring & Analisis Alur Onboarding/Lisensi)
- **Roadmap Fitur Masa Depan (Ditangguhkan):**
  - *Remote Screen Mirroring / Window Peek*:
    - Rencana fitur untuk menampilkan cuplikan layar PC atau jendela aktif di layar tablet/HP secara nirkabel.
    - Status: Ditangguhkan sementara untuk memprioritaskan alur konversi penjualan, stabilitas inti input deck, dan latensi ultra-rendah (1-3 ms).
    - Desain teknis masa depan yang disepakati: Menggunakan WebRTC on-demand (bukan streaming 60 FPS penuh tanpa henti) agar baterai tablet tidak cepat panas dan tidak membebani jaringan Wi-Fi lokal.
- **Rancangan Alur Pembelian & Autentikasi Pengguna (Zero-Friction Onboarding):**
  - *Pertimbangan Login Akun vs Kunci Lisensi (License Key)*:
    - Login akun (email/password) di aplikasi HP menambah friksi tinggi (*drop-off rate*) saat pengguna pertama kali mencoba menyambungkan perangkat di jaringan lokal.
    - Model yang direkomendasikan adalah **License Key + Email Magic Link**:
      1. Pengguna membeli paket di website utama (input email saat checkout).
      2. Sistem menerbitkan *License Key* dan link unduh installer server PC.
      3. Pengguna menjalankan server di PC -> PC menampilkan QR code untuk unduh APK ponsel dan otomatis memvalidasi lisensi.
      4. Ponsel langsung tersambung ke PC via PIN pairing lokal tanpa perlu repot mengetik username/password di layar kecil.

---

## 59. CATATAN CHECKPOINT (v0.9.55 - Harmonisasi AI Workstation di Ponsel & Kustomisasi Prompt Tombol HP)
- **Harmonisasi Tata Letak AI Workstation di Ponsel (Smartphone Landscape):**
  - Mengadaptasi Android-style Soft QWERTY Keyboard agar aktif di tablet maupun ponsel (`display: flex`).
  - Menghadirkan styling responsif compact untuk layar ponsel landscape (`max-height: 439px`):
    - Tuts keyboard disesuaikan ke tinggi 26px dan font 11.5px sehingga tidak menyebabkan overflow atau scrolling vertikal.
    - Tombol microphone disesuaikan ke 46x46px dengan ikon proporsional 22px.
    - Kotak transkripsi teks dibuat fleksibel (min-height 44px, max-height 72px).
  - Menambahkan fitur lipat/buka keyboard:
    - Tombol "Tutup" (`#btn-ai-tk-toggle`) pada bar kontrol keyboard untuk menyembunyikan keyboard saat pengguna membutuhkan ruang transkripsi lebih luas.
    - Tombol pintas "Keyboard" (`#btn-ai-open-kb`) pada header transkripsi untuk memunculkan kembali soft keyboard seketika.
    - Status visibilitas keyboard tersimpan di `localStorage` (`digi_ai_kb_collapsed`).
- **Akses Kustomisasi Tombol Prompt AI di HP & Tablet:**
  - Menambahkan tombol "Kustom" (`#btn-ai-edit-prompts-footer`) langsung pada footer kolom kiri AI Deck, tepat di samping badge "AI WORKSTATION".
  - Pengguna HP kini dapat mengkustomisasi 5 tombol prompt perintah (label nama dan teks prompt) dengan 1 sentuhan tanpa harus mencari tombol di dalam keyboard tablet.
  - Modal dialog kustomisasi prompt terhubung responsif dengan dukungan audio klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`).
  - Kamus terjemahan bilingual (`en` & `id`) diperbarui dengan key `ai_custom_prompts`, `ai_custom_prompts_title`, `ai_kb_hide`, `ai_kb_toggle_title`, `ai_kb_open`, `ai_kb_show_title`.

---

## 60. CATATAN CHECKPOINT (v0.9.56 - Relokasi Tombol Kustomisasi AI & Keandalan Deteksi Jendela PC Real-Time)
- **Penataan Ulang Tata Letak Ponsel (Mobile AI Workstation):**
  - Mengembalikan soft keyboard menjadi eksklusif untuk tablet (`@media (min-height: 440px)`). Pada ponsel (layar landscape), keyboard dinonaktifkan sehingga area transkripsi suara menjadi lega dan proporsional.
  - Menghapus tombol kustomisasi dari samping badge `AI WORKSTATION` pada kolom kiri. Badge dipulihkan penuh 100% lebar kolom sehingga tampilan kembali bersih dan eksklusif.
  - Memindahkan tombol kustomisasi prompt ke sisi kanan baris header transkripsi (`.ai-transcript-header`), berhadapan simetris dengan switcher bahasa dikte `[ ID | EN ]` menggunakan tombol pill minimalis `[ ✎ Kustom Prompt ]` (`#btn-ai-custom-prompt-header`).
  - Terhubung mulus dengan audio klik mekanikal (`playClickSound()`) dan getaran haptik (`vibe()`).
- **Keandalan Deteksi Jendela Aktif PC (Smart Context Anti-Miss):**
  - Menambahkan algoritma fallback X11 Stacking List (`_NET_CLIENT_LIST_STACKING`): Ketika fokus jendela mengembalikan `0x0` atau berada di jendela sistem internal (seperti desktop icons atau Host Manager), server secara cerdas mengambil jendela aplikasi pengguna teratas yang sedang aktif (misalnya Terminal).
  - Mengambil data jendela segar saat handshake WebSocket terhubung sehingga client yang baru tersambung/reconnect tidak pernah lagi menerima nilai basi `'Desktop'`.
  - Menambahkan handler WebSocket `get_active_window` (bebas hambatan pairing) yang otomatis dipanggil oleh frontend pada saat `ws.onopen` dan `visibilitychange`.
  - Mempercepat siklus pelacak konteks aplikasi dari 800ms menjadi 350ms untuk responsivitas instan.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 61. CATATAN CHECKPOINT (v0.9.57 - Fitur Remote Action Prompt / Smart Confirmation Card & Optimasi Modal About)
- **Optimasi Tombol Periksa Pembaruan (Modal About):**
  - Tombol "Periksa Pembaruan" (`#btn-check-update`) otomatis disembunyikan jika aplikasi sudah berada pada versi terbaru (`1.17.0`).
  - Sebagai gantinya, langsung ditampilkan status informasi badge hijau (`#about-update-status`): "Aplikasi Sudah Versi Terbaru (v1.17.0)" / "App is Up to Date (v1.17.0)".
  - Tombol unduh pembaruan hanya muncul jika terdeteksi versi baru yang lebih tinggi dari server/rilis.
- **Fitur Konfirmasi Jarak Jauh (Remote Action Prompt / Smart Confirmation Card):**
  - Memungkinkan konfirmasi atau pilihan input di Terminal (seperti `[y/N]`, pilihan prompt, approval CLI) maupun dialog aplikasi GUI desktop (dialog konfirmasi simpan, tutup, izin, prompt sistem) dikerjakan langsung dari ponsel/tablet tanpa harus berada di depan laptop/PC.
  - Backend (`server.py`):
    - Endpoint HTTP `POST /api/prompt` untuk menerima pemicu prompt konfirmasi dari skrip lokal, CLI, cron, atau agen, dengan dukungan opsi `wait=true` (menunggu respon pengguna di ponsel) dan `timeout`.
    - Endpoint HTTP `POST /api/prompt/dismiss` untuk membatalkan/menutup prompt.
    - Deteksi otomatis jendela dialog GUI X11/Windows (`_NET_WM_WINDOW_TYPE_DIALOG` / `WM_TRANSIENT_FOR` / `WS_EX_DLGMODALFRAME`) pada loop pelacak konteks `smart_context_tracker_loop()`.
    - Handler WebSocket `prompt_response` untuk mensimulasikan tombol/teks ke jendela PC aktif dan mem-broadcast penutupan prompt ke semua client terhubung.
    - Perkakas CLI mandiri `digi-prompt` (`chmod +x digi-prompt`) untuk integrasi mudah di terminal atau bash script.
  - Frontend (`static/index.html`):
    - Komponen UI `#modal-remote-prompt` (.remote-action-card) dengan badge aplikasi pengirim, teks pesan/perintah, grid tombol opsi dinamis (Primary/Danger/Default), dan timer hitung mundur jika berbatas waktu.
    - Listener WebSocket `remote_prompt` dan `remote_prompt_dismiss` untuk membuka dan menutup kartu konfirmasi secara responsif.
    - Dilengkapi umpan balik audio (`playPairingSuccessSound()`), bunyi klik mekanikal (`playClickSound()`), dan getaran haptik (`vibe([30, 40, 50])`).
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 62. CATATAN CHECKPOINT (v0.9.58 - Penyelarasan Posisi Mic AI Tengah & Rename Folder Proyek DigiSmartDeck)
- **Penyelarasan Vertikal Presisi Mic AI Workstation:**
  - Memperbaiki tata letak `.ai-mic-section` agar berada di tengah persis (geometris dan visual) di antara bar atas (`.top-bar`) dan kotak transkrip (`.ai-transcript-header` & `.ai-transcript-box`).
  - Mengeliminasi padding asimetris lama (`padding: 38px 2px 10px` pada desktop/tablet dan `padding: 6px 2px 3px !important` pada mobile).
  - Mengubah `.ai-mic-section` menjadi `flex: 1; min-height: 0; padding: 0 2px; gap: 5px; margin: auto 0; justify-content: center;` di seluruh ukuran layar (base, mobile landscape `@media (max-height: 439px)`, dan compact `@media (max-height: 420px)`).
  - Tombol mic dan label status kini menempati posisi tengah seimbang tanpa lagi mepet ke atas atau timpang dengan kotak teks transkrip.
- **Penyelarasan Nama Folder Proyek (`DigiSmartDeck`):**
  - Mengubah direktori proyek utama menjadi `DigiSmartDeck` (`/home/nino/ALI/project/DigiSmartDeck` dan `/home/nino/DigiSmartDeck`).
  - Mempertahankan symlink kompatibilitas penuh (`/home/nino/digikeyboard -> /home/nino/ALI/project/DigiSmartDeck`, `/home/nino/digismartdeck`, dan `/home/nino/ALI/project/digikeyboard`) agar service systemd Linux (`digikeyboard.service`), IDE workspace, dan skrip terminal tetap berjalan normal tanpa kendala.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 63. CATATAN CHECKPOINT (v0.9.59 - Rata Tengah Geometris Presisi Tombol Mic Antara Bar & Box di HP dan Tab)
- **Rata Tengah Vertikal Murni Tombol Mic Antara Top Bar dan Transcript Box:**
  - Memperbaiki tata letak `.ai-mic-section` dan tombol mic (`.ai-btn-mic`) di seluruh resolusi layar (HP landscape dan Tab) agar benar-benar berada di titik tengah seimbang (50% Y murni) di antara bar atas (`.top-bar`) dan kotak teks transkrip (`.ai-transcript-box`).
  - Menyatukan bar pemilih bahasa & prompt kustom (`.ai-transcript-header`) ke dalam kartu terpadu `.ai-transcript-box`, menghilangkan celah/displacement perantara yang sebelumnya membuat mic tampak lebih dekat ke bar atas.
  - Mengubah posisi label status `#ai-mic-status` menjadi `position: absolute; left: 50%; transform: translateX(-50%);` dengan kalkulasi offset presisi di bawah tepi tombol (`top: calc(50% + 48px)` pada tablet 86px, `top: calc(50% + 30px) !important;` pada mobile 52px, dan `top: calc(50% + 29px) !important;` pada compact 50px). Dengan demikian, label status tidak lagi mendesak tombol mic ke atas.
  - Menghapus aturan `margin: auto 0 !important;` dan padding sisa pada media query mobile (`@media (max-height: 439px)` dan `@media (max-height: 420px)`), memastikan flexbox centering beroperasi 100% murni dan konsisten di seluruh browser dan WebView Android.
- **Rata Tengah Horizontal Simetris:**
  - Menyeimbangkan kolom kiri dan kanan `.ai-main-grid` (`160px 1fr 160px` pada layar normal/tablet, `144px 1fr 144px` pada <=768px, dan `125px 1fr 125px` pada <=580px) sehingga kolom tengah berada tepat di tengah horizontal layar tanpa deviasi 16px seperti sebelumnya.
- **Optimasi Tablet Keyboard:**
  - Menghapus `margin-top: 6px` ganda pada `.ai-tablet-keyboard` sehingga ritme spasi vertikal antar elemen di kolom tengah tablet (`gap: 6px`) seragam dan seimbang.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 64. CATATAN CHECKPOINT (v0.9.60 - Relokasi Tombol Kustomisasi Prompt & Pembesaran Mic HP +30%)
- **Relokasi Tombol Kustomisasi Prompt AI:**
  - Menghilangkan tombol kustom prompt (`#btn-ai-custom-prompt-header`) dari header transkripsi audio.
  - Mengganti tombol Delete pada grid pintasan kolom kiri (`.ai-shortcuts-grid`) menjadi tombol "Kustom" (`#ai-btn-custom-prompt`) untuk membuka modal edit prompt.
  - Menata ulang dua baris teratas kontrol edit:
    - Baris 1: `[ Kustom | Cut ]`
    - Baris 2: `[ Copy | Paste ]`
- **Penskalaan Tombol Mic AI di HP (+30%):**
  - Memperbesar ukuran tombol mic (`.ai-btn-mic`) di tampilan ponsel landscape (`@media (max-height: 439px)`) sebesar ~30%, dari 52px menjadi 68px (ikon SVG diperbesar menjadi 32px).
  - Pada layar ultra-compact (`@media (max-height: 420px)`), diperbesar dari 50px menjadi 65px (ikon SVG 31px).
  - Menyesuaikan offset label status (`top: calc(50% + 38px) !important;`) sehingga tombol tetap rata tengah vertikal sempurna (50% Y) tanpa distorsi bentuk atau asimetri.
  - Ukuran mic pada layar tablet dan desktop tetap terkunci presisi di 86px asli.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 65. CATATAN CHECKPOINT (v0.9.61 - Eliminasi Tombol Kustomisasi di Soft Keyboard Tablet & Kunci Desain)
- **Eliminasi Tombol Kustomisasi pada Keyboard Lembut Tablet:**
  - Menghapus tombol duplikat edit prompt (`#ai-tk-btn-edit-prompt`) dari baris ke-4 soft QWERTY keyboard tablet.
  - Mengoptimalkan proporsi tuts spasi (`.ai-tk-key.ai-tk-space`) menjadi `flex: 3.5`, sehingga tata letak tuts baris bawah (mode angka, koma, spasi, titik, dan empat panah navigasi arah) menjadi rapi, simetris, dan proporsional.
  - Akses modal kustomisasi prompt kini terpusat secara konsisten dan eksklusif pada tombol "Kustom" (`#ai-btn-custom-prompt`) di kolom kiri.
- **Status Penguncian Desain:**
  - Desain tampilan UI untuk mode AI Workstation (baik tampilan HP maupun Tablet), mode Game Controller, dan mode Keyboard PC Standar telah dikonfirmasi matang dan resmi dikunci.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 66. CATATAN CHECKPOINT (v0.9.62 - Ikon Konfigurasi & Pembeda Visual Tombol Kustomisasi AI)
- **Ikon dan Aksen Visual Tombol Kustomisasi AI:**
  - Menambahkan ikon pensil konfigurasi SVG pada tombol Kustom (`#ai-btn-custom-prompt`) di grid pintasan kolom kiri.
  - Menerapkan styling khusus `.ai-btn-custom-tool` dengan aksen warna `--accent`, border lembut semi-transparan, dan tata letak horizontal ikon + teks.
  - Membedakan tombol Kustom secara visual dari tuts input pintasan langsung (seperti Cut, Copy, Paste), sehingga pengguna langsung memahami bahwa fungsinya adalah untuk membuka modal konfigurasi/kustomisasi tombol-tombol prompt AI.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 67. CATATAN CHECKPOINT (v0.9.63 - Pembukaan Instan Modal Kustomisasi & Penyederhanaan Notifikasi Pembaruan)
- **Respons Seketika Tombol Kustomisasi Prompt (Tanpa Ditahan):**
  - Mengubah penanganan event tombol Kustom (`#ai-btn-custom-prompt`) dari `bindAiKey` (yang sebelumnya memicu modal di `touchstart` sehingga pelepasan sentuhan `touchend` pengguna mengenai backdrop modal dan langsung menutupnya) menjadi standard click/tap listener dengan stopPropagation.
  - Menambahkan pengaman timestamp `lastModalOpenTime` pada `handleUniversalClose` (guard window 350ms) guna mencegah penutupan backdrop modal instan yang tidak disengaja oleh event sentuhan perangkat seluler.
  - Modal konfigurasi prompt kini langsung muncul seketika dalam satu kali klik/ketukan biasa tanpa perlu ditahan.
- **Penyederhanaan Notifikasi Pembaruan (Modal About):**
  - Menghilangkan teks versi `(${vStr})` dari label badge status pembaruan dan tombol unduh di bagian bawah modal About, karena versi aplikasi (`#about-app-version`) sudah ditampilkan secara jelas di bagian atas modal.
  - Teks kini bersih dan rapi: "Aplikasi Sudah Versi Terbaru" / "App is Up to Date" jika sudah mutakhir, atau "Pembaruan Tersedia - Unduh" / "Update Available - Download" jika terdapat rilis baru.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 68. CATATAN CHECKPOINT (v0.9.64 - Finalisasi & Penguncian Desain UI Mode AI, Game, Keyboard, dan Dialog Update)
- **Status Validasi & Penguncian Desain Menyeluruh:**
  - **Mode AI Workstation (HP & Tablet):**
    - Tombol Mic AI (`#btn-ai-mic`) berada 100% rata tengah secara geometris dan visual antara top bar (`.top-bar`) dan kotak transkrip (`.ai-transcript-box`).
    - Skala tombol Mic pada ponsel HP landscape (`@media (max-height: 439px)`) diperbesar ~30% menjadi 68px (ikon SVG 32px), dan pada ultra-compact menjadi 65px (ikon SVG 31px). Pada tablet dan desktop tetap terkunci di 86px asli.
    - Kolom kiri dan kanan seimbang simetris (`160px 1fr 160px`, `144px 1fr 144px`, `125px 1fr 125px`).
    - Grid kontrol edit ditata ulang rapi: Baris 1 `[ Kustom | Cut ]`, Baris 2 `[ Copy | Paste ]`.
    - Tombol Kustom (`#ai-btn-custom-prompt`) dilengkapi ikon pensil konfigurasi SVG dan aksen visual `.ai-btn-custom-tool`, serta langsung membuka modal dalam 1 kali klik/tap tanpa perlu ditahan.
    - Soft QWERTY keyboard tablet bersih dari tombol kustomisasi duplikat dengan tuts spasi proporsional (`flex: 3.5`).
  - **Mode Keyboard PC Standar & Game Controller:**
    - Tampilan dan fungsionalitas kedua mode telah divalidasi matang dan dikunci.
  - **Modal About & Dialog Pembaruan:**
    - Teks status pembaruan bersih dan bebas dari duplikasi nomor versi, karena versi aplikasi (`#about-app-version`) sudah tercantum di bagian atas modal.
  - **Struktur Repositori:**
    - Direktori resmi proyek bernama `DigiSmartDeck` dengan symlink backward-compatibility penuh untuk unit layanan systemd Linux (`digikeyboard.service`).
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 69. CATATAN CHECKPOINT (v0.9.65 - Integrasi Dialog Konfirmasi CLI Interaktif Multi-Opsi & Otomatisasi Dialog GUI Desktop Jarak Jauh)
- **Ekstensi CLI `digi-prompt` Multi-Opsi & Integrasi Shell/Terminal:**
  - Menambahkan argumen `--options` pada `digi-prompt` yang mendukung daftar opsi fleksibel (berupa format koma bebas seperti `--options "Izinkan Sekali,Selalu Izinkan,Tolak"` atau format array/objek JSON terstruktur).
  - Menyertakan dukungan parsing input via stdin (`digi-prompt -`) untuk piping langsung dari script atau terminal CLI.
  - Menambahkan argumen `-q / --value-only` untuk mengeluarkan nilai opsi terpilih secara murni ke stdout guna kemudahan integrasi dengan skrip bash/zsh/python.
  - Menambahkan opsi output `--json` untuk mencetak payload respons lengkap.
- **Deteksi Dialog GUI Desktop Kontekstual & Refocus Otomatis:**
  - Pada `server.py` (`smart_context_tracker_loop`), mendeteksi dialog sistem/aplikasi desktop secara otomatis berdasarkan kata kunci judul jendela (Save/Simpan: `Simpan (Enter)`, `Jangan Simpan (Alt+D)`, `Batal (Esc)`; Delete/Hapus: `Hapus (Enter)`, `Batal (Esc)`; Quit/Keluar: `Keluar (Enter)`, `Batal (Esc)`).
  - Pada penanganan `prompt_response`, server kini mengaktifkan dan memfokuskan kembali jendela target (`win_id`) secara presisi (`activate_and_focus_window`) sebelum mengirimkan tombol/kombinasi tombol, sehingga tindakan dialog GUI di PC tereksekusi akurat tanpa terganggu perpindahan jendela.
  - Mendukung simulasi kombinasi tombol berganda (`combo`, misal: `['alt', 'd']`).
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 70. CATATAN CHECKPOINT (v0.9.66 - Finalisasi Jalur PATH CLI digi-prompt, Optimasi Guard Modal Prompt, & Pembaruan Cache PWA v3)
- **Ketersediaan Perintah CLI Global:**
  - Utilitas `digi-prompt` telah di-symlink ke `~/.local/bin/digi-prompt`, sehingga dapat dieksekusi langsung dari terminal shell mana pun tanpa memerlukan path absolut.
- **Optimasi Guard Tampilan Modal Konfirmasi Interaktif:**
  - Menambahkan pengaman timestamp `lastModalOpenTime = Date.now()` pada `showRemotePrompt` untuk mencegah dismiss instan oleh listener universal sentuhan/backdrop seluler.
  - Memastikan elemen splash screen ditutup/dibersihkan secara tuntas saat menerima payload prompt jarak jauh, memastikan dialog selalu tampil di lapisan paling depan.
- **Pembaruan Service Worker & Invalidation Cache:**
  - Memperbarui `CACHE_NAME` pada `static/sw.js` menjadi `digismartdeck-cache-v3` guna menjamin pembaruan aset web dan logika dialog segera termuat di browser klien seluler/desktop tanpa terhambat cache lama.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 71. CATATAN CHECKPOINT (v0.9.67 - Penyempurnaan Modal Reconnecting: Ikon Kaca Pembesar, Teks Bersih, & Animasi Titik Looping)
- **Desain & Ikonografi Modal Reconnecting (`#reconnect-banner`):**
  - Mengganti ikon lingkaran putar dengan ikon SVG Kaca Pembesar (Search / Magnifying Glass) yang presisi di dalam cincin radar pulse (`.rc-modal-pulse`).
- **Penyederhanaan Teks & Animasi Titik Loading:**
  - Menghilangkan teks hitungan percobaan retry `(5x)` yang mengganggu.
  - Judul diubah menjadi `Menghubungkan` (Bahasa Indonesia) / `Connecting` (Bahasa Inggris) disertai animasi titik loading (`.rc-dots`) yang berulang secara mulus: `.` -> `..` -> `...` -> `.` (looping dinamis hingga terhubung).
  - Mengatur elemen `.rc-dots` dengan lebar tetap (`min-width: 18px`) dan perataan kiri agar teks tidak berguncang secara horizontal saat jumlah titik berganti.
  - Kalimat deskripsi di bawahnya diperbarui menjadi: "Memindai seluruh jalur koneksi" (ID) / "Scanning all connection paths" (EN).
- **Pembaruan Cache Service Worker:**
  - Memperbarui versi cache PWA di `static/sw.js` menjadi `digismartdeck-cache-v4`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 72. CATATAN CHECKPOINT (v0.9.68 - Implementasi Smart Terminal Supervisor 'digi-term' & One-Click Companion Launcher)
- **Modul Smart Terminal Supervisor (`digi-term`):**
  - Mengembangkan supervisor pseudoterminal (PTY) mandiri di `/home/nino/digikeyboard/digi-term` (di-symlink ke `~/.local/bin/digi-term`).
  - Secara otomatis memantau aliran teks keluar anak proses dan mendeteksi berbagai pola pertanyaan/konfirmasi interaktif (konfirmasi biner `[Y/n]`, menu pilihan bernomor `1) ... 2) ...`, verifikasi agen coding AI seperti Antigravity/Gemini/Claude Code/Aider, serta perintah lanjut `Press Enter`).
  - Mengirimkan pertanyaan tersebut secara real-time ke aplikasi DigiSmartDeck di HP sebagai kartu pilihan sentuh interaktif.
  - Menyuntikkan respon yang dipilih pengguna di HP langsung ke stdin PTY terminal tanpa mengganggu fokus jendela desktop lain. Mengetik langsung di keyboard fisik PC secara otomatis menutup kartu prompt di HP.
- **Penyederhanaan One-Click untuk Pengguna Awam (Vibe Coders):**
  - **Di Klien Web / Mobile:** Menambahkan tombol chip `Smart Terminal` di Menu Deck (Sistem & Utilitas) yang membuka dialog persetujuan (consent modal) transparan. Setelah disetujui, jendela terminal pintar otomatis terbuka di PC dengan satu sentuhan.
  - **Di Desktop GUI Manager (`digikeyboard_gui.py`):** Menambahkan kartu peluncur `TERMINAL PINTAR (VIBE CODING & DEVELOPER COMPANION)` yang memungkinkan peluncuran terminal terawasi dengan satu kali klik.
  - Persetujuan akses disimpan secara transparan dan etis di `data/terminal_consent.json`.
- **Pembaruan Service Worker:**
  - Versi cache PWA pada `static/sw.js` diperbarui ke `digismartdeck-cache-v5`.
- **Kepatuhan Aturan Mutlak:**

---

## 73. CATATAN CHECKPOINT (v0.9.69 - Eliminasi Tombol Manual Smart Terminal & Integrasi Shell Hook Otomatis Saat Instalasi)
- **Eliminasi Tombol Manual Smart Terminal (Zero Clutter):**
  - Menghapus tombol chip `#btn-smart-terminal` dari Menu Deck utilitas dan modal persetujuan `#modal-smart-term` di antarmuka web/mobile (`static/index.html`). Ponsel murni berfungsi sebagai penerima kartu pilihan interaktif tanpa tombol peluncur yang canggung.
  - Menghapus kartu peluncur manual terminal di desktop GUI manager (`digikeyboard_gui.py`).
- **Integrasi Izin Akses Saat Penginstalasian Awal (`install-linux.sh`):**
  - Skrip instalasi host Linux (`install-linux.sh`) kini menyertakan langkah persiapan integrasi Smart Terminal.
  - Mengonfirmasi izin akses pengguna di awal ("Aktifkan Smart Terminal otomatis? [Y/n]").
  - Memasang hook shell di `~/.bashrc` (dan `~/.zshrc`):
    `if [[ $- == *i* && -t 0 && -t 1 && -z "$DIGI_TERM_SUPERVISED" && -z "$DIGI_TERM_DISABLE" && -f "$HOME/.config/digismartdeck/smart_terminal_enabled" && -x "$HOME/.local/bin/digi-term" ]]; then exec "$HOME/.local/bin/digi-term"; fi`
  - Proteksi penuh: skrip non-interaktif, cron job, subshell, dan perintah otomatis tidak terpengaruh sama sekali.
- **Manajemen Status di Host Manager (`digikeyboard_gui.py`):**
  - Pada Tab Setup Wizard & Layanan, ditambahkan indikator "Integrasi Smart Terminal Otomatis: AKTIF / NONAKTIF" serta tombol alih kontrol izin sistem.
- **Pembaruan Service Worker:**
  - Cache Service Worker di `static/sw.js` diperbarui ke `digismartdeck-cache-v6`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 74. CATATAN CHECKPOINT & STRATEGI FINALISASI MVP (v0.9.70 - Reposisi Produk, Strategi Harga & Rencana Kerja Peluncuran)
- **Reposisi Kategori Produk & Target Market (Vibe Coding Companion):**
  - Identitas Produk: **AI Workstation & Vibe Coding Companion**.
  - Masalah Inti (Core Pain Point): Mengeliminasi kelelahan fisik developer dan vibe coder yang harus duduk terpaku menatap layar monitor saat agen AI (Antigravity, Claude Code, Cursor, Aider, Devin) sedang melakukan multi-step coding dan meminta konfirmasi interaktif (`[Y/n]`, approval file edit, shell command).
  - Solusi Unik (USP): DigiSmartDeck menjadi infrastruktur fisik kendali jarak jauh (Human-in-the-Loop) tingkat sistem operasi (OS-level / Linux PTY & uinput). Pengguna dapat santai di kasur atau sofa sambil menyetujui perintah terminal atau mendikte prompt suara panjang lewat ponsel dengan latensi <1ms.
- **Strategi Penetapan Harga (Pricing & Monetization Strategy):**
  - *Anchor Pricing (Nilai Patokan Resmi):* Rp 450.000 (~$29.00 USD).
  - *Harga Resmi & Peluncuran Perdana (Launch Offer):*
    - Pasar Domestik (Indonesia via QRIS/Mayar): Rp 25.000 / bulan dan Rp 250.000 untuk Lisensi Seumur Hidup (Lifetime Pro).
    - Pasar Global (Gumroad / LemonSqueezy): $29.00 Lifetime Pro ($2.50 / bulan).
    - Akses Awal: Free Trial 7 Hari penuh tanpa batasan fitur untuk membentuk kebiasaan kerja (habit-forming).
- **Daftar Pekerjaan Rumah (PR) Menuju Peluncuran Penuh (Target: Besok):**
  - **PR 1: Desain Ulang Komprehensif Host GUI PC (`digikeyboard_gui.py`):**
    - Masalah Saat Ini: Tampilan GUI manager di desktop PC masih terasa kaku, tata letak visual kurang menjual, dan kata-kata/diksi teknis belum profesional.
    - Solusi: Merombak gaya antarmuka, hierarki visual, warna obsidian/accent, dan tata bahasa profesional agar selaras sempurna (matching) dengan standar kemewahan Web & Mobile Client.
  - **PR 2: Penyempurnaan Teks & Alur Installer Linux (`install-linux.sh`):**
    - Menyempurnakan bahasa terminal installer agar bersih, profesional, to-the-point, dan berorientasi nilai produk komersial.
  - **PR 3: Sistem Token Aktivasi Lisensi Pro (`auth_manager.py`):**
    - Memastikan generator kunci lisensi, validasi offline HMAC-SHA256, dan alur aktivasi pro di PC host dan ponsel berjalan mulus tanpa kendala teknis.
  - **PR 4: Marketing Kit & Landing Page:**
    - Menyusun materi pemasaran, rancangan landing page promosi, video demonstrasi 30 detik (vibe coding santai dari kasur sambil approve terminal di HP), dan panduan instalasi.
  - **Transisi Fase:**
    - Menutup tahap produksi dan pengembangan fitur MVP.
    - Beralih penuh ke tahap finishing kemasan, aktivasi lisensi komersial, dan peluncuran pemasaran.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 75. CATATAN CHECKPOINT (v0.9.71 - Perbaikan Bug Kombinasi Tombol Dialog GUI & Ekspansi Deteksi Prompt Terminal AI Agent)
- **Perbaikan Eksekusi Kombinasi Tombol Dialog GUI (`server.py`):**
  - Mengatasi bug fatal `NameError: name 'simulate_key' is not defined` pada penanganan `prompt_response` dengan mengimplementasikan fungsi `simulate_combo(keys)`.
  - Fungsi `simulate_combo` menekan modifier dan tombol utama secara berurutan menggunakan `simulate_press`, menunggu jeda 40ms, lalu melepasnya dalam urutan terbalik menggunakan `simulate_release`.
  - Membungkus seluruh blok penanganan simulasi input `prompt_response` dengan `try...except` guna mencegah putusnya koneksi WebSocket akibat kesalahan simulasi.
  - Dialog "Save Changes" pada Note/Catatan kini mengeksekusi `Alt+D` secara hardware-level melalui uinput, sehingga tombol "Jangan Simpan" (Discard) langsung aktif tanpa salah mencentang kotak checklist.
- **Ekspansi Cerdas Deteksi Prompt CLI & Agen AI (`digi-term`):**
  - Memperbarui fungsi `detect_prompt` pada supervisor PTY pseudoterminal:
    - Mendukung format prompt tri-state dan biner agen AI: `[y/n/a]`, `(y/n/always)`, `(y)es, (n)o, (a)lways`, `[Y/n]`. Jika opsi `a` (always) terdeteksi, opsi "Selalu Izinkan" otomatis disertakan pada kartu di tablet/ponsel.
    - Mendukung menu bernomor multi-baris yang berakhir pada opsi terakhir tanpa memerlukan baris "Choice:" terpisah.
    - Mendukung antarmuka TUI selector berbasis kursor/panah (`❯ 1. Yes`, `> 1. Yes`).
    - Mendukung analisis konteks kalimat izin AI agen (`allow`, `approve`, `permission`, `run this command`, `execute this`) dalam 8 baris terakhir.
- **Validasi dan Pengujian:**
  - 11 variasi pengujian prompt (biner, tri-state, menu bernomor, pertanyaan izin agen, dan TUI) lulus uji 100%.
  - Layanan `digikeyboard.service` telah direstart dan aktif melayani koneksi klien seluler.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 76. CATATAN CHECKPOINT (v0.9.72 - Perbaikan Double Enter pada Perintah Slash & Debounce Tuts Enter AI Workstation)
- **Akar Masalah Double Enter pada Perintah Slash (seperti `/model`):**
  1. *Spasi Tambahan Sebelum Enter*: Pada `ai-btn-enter`, pengiriman teks sebelumnya menyertakan spasi trailing (`textToSend + ' '`). Pada CLI interaktif (seperti Antigravity CLI, Claude Code), perintah slash yang diakhiri spasi langsung memicu mode autokomplit/daftar opsi dropdown. Ketika tombol Enter hardware dikirim 5ms kemudian, Enter tersebut langsung memilih opsi pertama yang sedang tersorot.
  2. *Ghost Mousedown Event*: Pada `bindAiKey`, ketiadaan `e.preventDefault()` pada `touchstart` memungkinkan browser seluler mensintesis event `mousedown` tiruan dengan jeda waktu di atas ambang batas lama, sehingga fungsi eksekusi tombol terpanggil dua kali berturut-turut.
  3. *Ketiadaan Debounce di Tombol Enter*: Tombol `#ai-btn-enter` belum memiliki pengaman selang waktu (cooldown window) saat menerima ketukan cepat.
- **Solusi yang Diterapkan:**
  1. *Eliminasi Spasi Trailing Sebelum Enter*: Teks dikirim secara murni (`sendAiText(textToSend)`) tanpa imbuhan spasi di belakangnya saat menekan Enter, sehingga perintah slash seperti `/model` tereksekusi bersih tanpa memicu dropdown instan.
  2. *Pengaman Event Touch & Debounce Global (`bindAiKey`)*:
     - Menambahkan `e.preventDefault()` pada `touchstart` untuk menghentikan sintesis event `mousedown` dan `click` tiruan di peramban mobile/WebView.
     - Menerapkan pengaman selang waktu `lastTriggerTime` (320ms) agar aksi tuts tidak dapat terpicu ganda.
  3. *Debounce Khusus Tombol Enter (`lastAiEnterTime`)*: Menambahkan batas cooldown 400ms pada penanganan klik `#ai-btn-enter`.
  4. *Pembaruan Versi Cache PWA*: Versi cache di `static/sw.js` diperbarui ke `digismartdeck-cache-v11`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 77. CATATAN CHECKPOINT (v0.9.73 - Standarisasi Pop-up Terminal CLI & 4 Tombol Izin: Yes, Allow in this chat, Allow in this project, No)
- **Akar Masalah Pop-up Terminal Sebelumnya Muncul 2 Pilihan & Kadang Tidak Aktif:**
  1. *Hardcoded Opsi Biner Lama di digi-term*: Versi lama `digi-term` memiliki blok penanganan kata kunci izin AI yang secara eksplisit hanya mengembalikan 2 opsi (`['Izinkan', 'Tolak']`), sehingga mengabaikan opsi per-chat atau per-proyek.
  2. *Proses Shell Lama Masih Aktif di Memori*: Sesi terminal yang dibuka sebelum modifikasi kode masih menjalankan skrip lama di memori hingga terminal dimuat ulang.
  3. *Interferensi Animasi Spinner & Blink Cursor ANSI*: Output escape sequence terminal yang terus-menerus terkirim pada jeda waktu ~100ms membuat pewaktu `last_output` terus tereset, sehingga deteksi idle tidak pernah mencapai ambang batas pemicuan.
  4. *Buffer Baris Terakhir Kursor Murni*: Pada CLI interaktif, baris terakhir sering kali hanya berisi karakter prompt tunggal (`> `, `: `, `? `, `$ `), sehingga regex lama menganggapnya sebagai prompt shell biasa dan mengabaikan pertanyaan pada baris sebelumnya.
- **Solusi yang Diterapkan:**
  1. *Standarisasi 4 Kunci Jawaban Resmi AI CLI*:
     - `Yes`: Eksekusi satu kali (kirim `1\n` atau `y\n`, tombol primer).
     - `Allow in this chat`: Izin untuk sesi percakapan aktif (kirim `2\n` atau `c\n`).
     - `Allow in this project`: Selalu izinkan untuk seluruh direktori proyek (kirim `3\n` atau `a\n`).
     - `No`: Tolak / batalkan eksekusi (kirim `4\n` atau `n\n`, tombol bahaya).
     - Menangani pemetaan otomatis baik untuk menu bernomor (`1`, `2`, `3`, `4`) maupun prompt berbasis huruf.
  2. *Tata Letak Grid Simetris 2x2 di Mobile (`static/index.html`)*:
     - Mengubah `.rap-options-container` menjadi `grid-template-columns: repeat(2, 1fr)` agar keempat tombol tersusun seimbang (2 baris x 2 kolom) di layar ponsel.
  3. *Penyaringan ANSI & Pewaktu Responsif*: Hanya karakter teks non-ANSI yang memperbarui `last_output`, dengan batas jeda responsif 0.22 detik.
  4. *Inspeksi Mundur Baris Pertanyaan & Judul Deskriptif (`extract_prompt_details`)*:
     - Mendeteksi pertanyaan aksi (`ask for permission`, `run this command`, `execute this command`, `allow`).
     - Menampilkan judul spesifik pada dialog kartu (`Run This Command?`, `Ask for Permission`, `Allow This Action?`).
     - Menampilkan isi perintah terminal dengan font monospace dan container scrollable (`max-height: 200px`).
  5. *Re-broadcast Prompt Aktif pada Reconnect WebSocket (`server.py`)*: Setiap klien seluler yang menyambung kembali langsung menerima siaran instan daftar prompt tertunda (`PENDING_PROMPTS`).
  6. *Pembaruan Versi Cache PWA*: Versi cache di `static/sw.js` diperbarui ke `digismartdeck-cache-v13`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 78. CATATAN CHECKPOINT (v0.9.74 - Tata Letak Pop-up Izin Satu Baris Simetris & Mode Fullscreen HP)
- **Tata Letak Tombol Pop-up Izin Satu Baris Simetris (`.rap-options-container`):**
  - Mengubah wadah tombol opsi pop-up izin menjadi satu baris horizontal murni (`display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: 8px;`).
  - Seluruh tombol aksi (baik 2 tombol maupun 4 tombol resmi AI: Yes, Allow in this chat, Allow in this project, No) tersusun berdampingan dalam satu baris datar yang 100% simetris dengan lebar merata seimbang.
  - Pada layar tablet / desktop (`min-height: 481px`), pop-up berwujud kartu mengambang elegan berlebar luas (`width: min(640px, 94vw); max-width: 640px;`).
- **Mode Fullscreen Nyaman pada Layar Ponsel HP Landscape (`@media (max-height: 480px)`):**
  - Memanfaatkan layar penuh ponsel (`width: 100vw; height: 100vh; border-radius: 0; border: none;`) sehingga tampilan tidak berdesakan dan nyaman dioperasikan dengan dua tangan.
  - Header kartu menempati sisi atas dengan badge pengirim aplikasi (`.rap-app-badge`), judul konfirmasi, dan tombol tutup '✕'.
  - Kotak pesan/perintah (`.rap-message-box`) mengisi area tengah yang fleksibel dengan pembatas tinggi dan scrollbar vertikal halus (`overflow-y: auto; -webkit-overflow-scrolling: touch;`). Teks panjang tidak dipaksakan tampil sekaligus melainkan dapat digulir (scrolling) untuk meninjau perintah atau data yang dimintakan izin.
  - Tombol aksi tetap tersusun satu baris simetris di bagian paling bawah kartu dengan target sentuhan jari yang ergonomis.
- **Pembaruan Service Worker:**
  - Versi cache PWA pada `static/sw.js` diperbarui ke `digismartdeck-cache-v14`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 79. CATATAN CHECKPOINT (v0.9.75 - Tombol Pop-up Izin Bersih Tanpa Huruf & Penguatan Keamanan Endpoint Server)
- **Tombol Izin Bersih Murni Kata Kunci (Zero Letter Badges):**
  - Tampilan tombol pada dialog izin (`showRemotePrompt`) di `static/index.html` kini hanya memuat kata kunci utama (misal: `Yes`, `Allow in this chat`, `Allow in this project`, `No`, `Ya`, `Batal`, `Lanjut`).
  - Pembersihan otomatis regex pada label untuk membuang seluruh imbuhan shortcut dalam kurung seperti `(Enter)`, `(Esc)`, `(1)`, `(2)`, `(y/n)`.
  - Penghapusan elemen `rap-btn-sub` sehingga tidak ada lagi badge huruf atau hotkey sekunder yang membingungkan pengguna di layar sentuh ponsel.
  - Penyelarasan orientasi baris horizontal (`flex-direction: row`) pada `.rap-btn` untuk keterbacaan teks yang lebih rapi dan seimbang.
- **Penguatan Keamanan Endpoint & WebSocket (`server.py`):**
  - *Restriksi Localhost pada Endpoint Sensitif*:
    - `GET /api/pairing/pin`: Wajib localhost (`127.0.0.1`, `::1`). Mengembalikan `403 Forbidden` jika diakses dari jaringan LAN eksternal, mencegah pihak asing mencuri PIN pairing tanpa melihat layar fisik PC.
    - `POST /api/prompt` & `POST /api/prompt/dismiss`: Wajib localhost. Menolak permintaan eksternal sehingga perintah CLI atau injeksi tindakan hanya sah berasal dari aplikasi lokal PC host (`digi-term`, shell skrip lokal).
    - `POST/GET /api/test/reconnect`: Wajib localhost, mencegah gangguan pemutusan koneksi massal dari jaringan luar.
  - *Perlindungan Akses WebSocket*:
    - `prompt_response`: Memverifikasi status pairing perangkat sebelum mengeksekusi simulasi input tombol atau kombo ke PC host.
    - `get_pairing_info` & `unpair_device`: Menolak akses jika belum diautentikasi dan menyembunyikan PIN rahasia jika permintaan bukan dari localhost.
    - `broadcast_prompt`: Menapis siaran pesan prompt aktif sehingga hanya terkirim ke klien yang telah berstatus terotorisasi (`ws['authorized'] = True`).
- **Pembaruan Service Worker:**
  - Versi cache PWA pada `static/sw.js` diperbarui ke `digismartdeck-cache-v15`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 80. CATATAN CHECKPOINT (v0.9.76 - Audit & Pengerasan Keamanan Menyeluruh / Comprehensive Security Hardening)
- **Mitigasi Serangan Brute-Force PIN & Timing Attack (`auth_manager.py`):**
  - Menerapkan penalti lockout bertingkat berbasis IP per-klien pada `verify_and_register`:
    - 5 kali percobaan gagal berturut-turut memicu penguncian sementara selama 30 detik.
    - 10 kali percobaan gagal memicu penguncian selama 300 detik (5 menit).
  - Mengganti pencocokan string PIN biasa dengan `hmac.compare_digest(clean_pin, self.pin)` untuk memusnahkan kerentanan timing attack.
  - Menambahkan pembatasan laju aktivasi lisensi (`failed_license_attempts`) untuk mencegah brute-force serial key.
- **Pengamanan Izin Berkas Sensitif di Disk (File Permissions):**
  - File basis data lokal `data/paired_devices.json` dan `data/license.json` kini secara otomatis disetel dengan izin ketat `0o600` (`rw-------`). Hanya akun pengguna Linux yang menjalankan proses server yang memiliki akses baca/tulis terhadap secret token perangkat dan lisensi.
- **Sanitasi Ketat Window ID & Mitigasi Command/Flag Injection (`server.py`):**
  - Menambahkan validator `is_valid_window_id(win_id)` dengan regex `^(0x[0-9a-fA-F]+|\d+)$`.
  - Fungsi `activate_and_focus_window`, `minimize_window`, `maximize_window`, dan `close_window` menolak secara mutlak argumen ilegal sebelum diteruskan ke utilitas `wmctrl` atau pustaka ctypes X11.
- **Validasi Batasan Input WebSocket & Proteksi DoS:**
  - Menyetel `max_msg_size=131072` (128 KB) pada `WebSocketResponse` guna mencegah serangan eksploitasi memori buffer via paket berukuran raksasa.
  - Sanitasi panjang teks pada `type_text` dibatasi maksimal 5.000 karakter per pesan untuk mencegah penguncian loop simulasi input.
  - Menambahkan pengecekan `math.isfinite` dan clamping koordinat pada pesan `mousemove` (-2000 s/d 2000 px), `mouseabs` (0.0 s/d 1.0), `mousescroll` (-500 s/d 500), serta `volume_set` (0 s/d 100).
  - Membatasi jumlah tombol dalam perintah `combo` maksimal 10 tombol.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 81. CATATAN CHECKPOINT (v0.9.77 - Sanitasi Repositori Git Pre-Deployment & Pencegahan Kebocoran Data)
- **Eliminasi Kebocoran Data Perangkat & Lisensi Lokal dari Git:**
  - Menghapus pelacakan berkas runtime `data/paired_devices.json` dan `data/license.json` dari repositori Git (`git rm --cached`). Berkas ini sebelumnya memuat IP lokal pengguna (`192.168.8.100`), fingerprint perangkat keras ponsel (`HONORHEY3-W09`), dan token autentikasi rahasia.
  - Menambahkan aturan `data/*` dan `!data/.gitkeep` ke `.gitignore` serta membuat `data/.gitkeep` agar folder basis data tetap terbentuk otomatis saat clone baru tanpa membocorkan data pribadi.
- **Portabilitas Skrip & Sanitasi Hardcoded Path Pengembang:**
  - *`build-apk.sh`*: Mengganti path hardcoded `/home/nino/...` dengan `$HOME` (`$HOME/.local/share/jdk` dan `$HOME/Android/sdk`).
  - *`install-linux.sh`*: Mengganti path `/home/nino/digikeyboard/...` pada file `.desktop` menjadi `$SCRIPT_DIR` yang dinamis di folder instalasi mana pun.
  - *`digikeyboard_gui.py`*: Mengubah perintah restart server agar menggunakan path skrip dinamis `os.path.abspath(__file__)` dan `pkill -f "server.py"`.
- **Sanitasi Klien Android & Komentar UI:**
  - *`MainActivity.java`*: Mengganti default IP statis pengembang `http://192.168.8.102:8080` menjadi IP generik `http://192.168.1.100:8080`.
  - *`static/index.html`*: Membersihkan komentar informal di template mode kustom menjadi komentar formal profesional `<!-- Mode Kustom View Template -->`.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 82. CATATAN CHECKPOINT (v0.9.78 - Keamanan & Privasi Mutlak sebagai Nilai Jual Komersial Utama)
- **Reposisi Keamanan & Privasi sebagai Unique Selling Proposition (USP):**
  - Mengintegrasikan pilar privasi murni (Privacy-First & Zero-Telemetry) ke dalam materi komersial, dokumentasi, dan antarmuka Store Modal.
  - Menegaskan pembeda utama DigiSmartDeck dibanding aplikasi kontrol nirkabel cloud yang rawan keylogging atau pelacakan telemetri pihak ketiga.
- **Pembaruan Dokumentasi Komersial & Teknis:**
  - *`PROJECT_CONTEXT.md`*: Menambahkan pilar ke-5 pada bagian Nilai Jual Utama (USP) di AI Workstation & Controller.
  - *`docs/COMMERCIAL_GUIDE.md`*: Menambahkan poin ke-4 pada Keunggulan Visual & Kompetitif serta matriks perbandingan privasi.
  - *`README.md`*: Menambahkan fitur ke-15 ("Keamanan & Privasi Mutlak / Zero-Telemetry & 100% On-Premise") yang merinci nol pencatatan ketikan, ketiadaan server perantara, dan kesiapan mode air-gapped.
- **Integrasi Trust Badge di Store Modal (`static/index.html`):**
  - Menambahkan kartu jaminan privasi (Privacy-First Guarantee Badge) di bagian atas katalog Store Modal.
  - Menyertakan kunci terjemahan bilingual `store_privacy_badge` untuk Bahasa Inggris (`I18N.en`) dan Bahasa Indonesia (`I18N.id`).
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 83. CATATAN CHECKPOINT (v0.9.79 - Presisi Waktu Pop-up Terminal: Eliminasi Pop-up Prematur & Pop-up Usang)
- **Akar Masalah Pop-up Izin Muncul di Waktu yang Salah:**
  1. *Muncul Terlalu Awal (Prematur)*: Bypass `is_priority` sebelumnya mengabaikan jeda tunggu diam (`idle < IDLE_SECONDS`). Begitu terminal mencetak log yang memuat kata kunci seperti `run`, `command`, atau `permission` saat proses baru mulai streaming, pop-up langsung ditembakkan seketika sebelum proses berhenti menunggu input pengguna.
  2. *Muncul Terlalu Lambat (Usang/Stale)*: Buffer historis terminal menyimpan 3.072 karakter lama. Ketika perintah selesai dan shell kembali ke prompt biasa (`(venv) user@host:~$`), detektor membaca 15 baris ke belakang dan mendeteksi kembali pertanyaan yang sudah selesai. Selain itu, saat pengguna menjawab langsung di PC atau proses bergerak maju, kartu aktif di HP tidak di-dismiss.
  3. *Akumulasi di Server*: Cache `PENDING_PROMPTS` di `server.py` menyimpan prompt tanpa TTL pembersihan otomatis, sehingga saat HP reconnect, prompt lama dikirim ulang.
- **Solusi yang Diterapkan:**
  1. *Wajib Menunggu Terminal Diam (Enforce Idle Settling Time di `digi-term`)*: Menghapus total bypass `is_priority`. Terminal wajib stabil dan diam (`idle >= 0.28s`) sebelum buffer diproses.
  2. *Pemeriksaan Kursor Aktif Terbawah (Anchor to Active Bottom Prompt)*:
     - Mendeteksi prompt shell biasa (bash, zsh, fish, venv, PowerShell) via `is_shell_prompt()`. Jika baris terakhir adalah shell prompt, segera tolak/abaikan.
     - Pertanyaan izin atau pilihan hanya valid jika berada tepat di baris aktif paling bawah (`tail`) terminal.
  3. *Auto-Dismiss saat Output Baru Mengalir*: Begitu child process mencetak teks baru yang signifikan pada `master_fd`, supervisor langsung memanggil `dismiss_active()` dan membersihkan buffer, menutup kartu di HP secara instan.
  4. *Pembersihan TTL di Server (`cleanup_pending_prompts` di `server.py`)*: Membersihkan entri yang berusia lebih dari batas timeout (maks 60s) secara periodik dan sebelum dikirimkan ulang ke client WebSocket yang baru terhubung.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 84. CATATAN CHECKPOINT (v0.9.80 - Standardisasi Tampilan APK Sesuai Benchmark Chrome Mobile & Landing Page MVP)
- **Standardisasi Tampilan APK 100% Identik dengan Chrome Mobile:**
  - Menghilangkan tombol overlay native Android (`btnServerSettings` ImageButton) dari `activity_main.xml` dan `MainActivity.java` sehingga area WebView 100% murni tanpa elemen asing.
  - Mengonfigurasi `WebSettings` di `MainActivity.java` dengan `setUseWideViewPort(true)`, `setLoadWithOverviewMode(true)`, `setSupportZoom(false)`, dan `setDisplayZoomControls(false)` agar rendering viewport, rasio DPI, dan penskalaan elemen di APK bekerja persis seperti peramban Chrome mobile.
  - Mengembalikan styling CSS `.top-bar` dan `.deck-trigger-btn` di `static/index.html` sesuai patokan Chrome.
- **Isolasi Fitur Smart Confirmation untuk MVP:**
  - Memisahkan kode eksperimen Smart Confirmation ke branch terisolasi `feature/smart-confirmation`.
  - Menambahkan flag `ENABLE_REMOTE_PROMPTS = os.environ.get('DIGI_ENABLE_PROMPTS', '0') == '1'` di `server.py` yang secara default bernilai `False` untuk memastikan kestabilan peluncuran MVP.
- **Penyediaan Halaman Landing Page Komersial MVP:**
  - Membangun landing page mandiri `static/landing.html` dan `landing/index.html` dengan desain modern responsif, showcase mockup interaktif, matriks perbandingan harga (Rp 25.000/bln vs Rp 250.000 Lifetime Pro), dan tombol unduh APK langsung.
  - Menambahkan endpoint rute di `server.py`: `/landing`, `/landing.html`, `/about`, dan `/download/apk`.
- **Kompilasi Ulang APK:**
  - APK berhasil dikompilasi ulang via `./build-apk.sh` ke `dist/DigiSmartDeck.apk` dan `static/DigiSmartDeck.apk` dengan ukuran ringkas 5.4 MB.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 85. CATATAN CHECKPOINT (v1.18.0 - Penerapan Standar Industri Versioning SemVer 2.0.0 & Otomasi Sinkronisasi Multi-Platform)
- **Standardisasi Versioning Industri IT (SemVer 2.0.0):**
  - Mengadopsi prinsip Semantic Versioning (`MAJOR.MINOR.PATCH`):
    * `PATCH`: Perbaikan bug atau penyesuaian styling minor (misal: 1.18.0 -> 1.18.1).
    * `MINOR`: Penambahan fitur baru backward-compatible (misal: peluncuran landing page, mode baru, standarisasi viewport APK: 1.17.0 -> 1.18.0).
    * `MAJOR`: Perubahan arsitektur besar atau breaking changes (misal: 1.x -> 2.0.0).
- **Single Source of Truth (SSOT) Versi:**
  - File root `VERSION` menjadi rujukan tunggal seluruh komponen proyek.
  - `android/app/build.gradle` kini secara dinamis membaca file `VERSION`, mengompilasi `versionName` (string versi SemVer) dan menghitung `versionCode` secara matematis (`major * 10000 + minor * 100 + patch`, misal 1.18.0 -> `11800`), memenuhi standar resmi Google Play Store dan Android package manager.
  - Server Python (`server.py`) memuat versi via `load_version()` dari file `VERSION` dan mengeksposnya ke endpoint `/api/version`.
- **Penyempurnaan Skrip Otomasi `bump-version.sh`:**
  - Menghapus 100% karakter emoji dari skrip dan log keluaran terminal guna menaati aturan repositori.
  - Melakukan sinkronisasi otomatis ke semua aset: `VERSION`, `CHANGELOG.md`, `static/index.html` (badge fallback), `static/landing.html` dan `landing/index.html` (badge `PRO V...`).
  - Menjalankan `./build-apk.sh` secara otomatis setiap terjadi bump versi sehingga file distribusi APK selalu mutakhir.
  - Membuat git commit dan git tag versi resmi secara otomatis.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 86. CATATAN CHECKPOINT (v1.18.1 - Perbaikan Continuous Mic Google Voice Typing & Redaman Chime)
- **Perpanjangan Jendela Silence Timeout:**
  - `EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS` dinaikkan ke 6000ms.
  - `EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS` dinaikkan ke 5000ms.
  - `EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS` disetel ke 10000ms.
  - Pengguna dapat berhenti sejenak untuk berpikir tanpa mic langsung mati tergesa-gesa.
- **Penyelamatan Teks Interim saat Restart:**
  - Ditambahkan fungsi `promoteInterimToFinal()` pada JavaScript klien dan callback `onNativeSpeechRestart()`.
  - Kata-kata yang sedang terucap saat sesi timeout/restart tidak pernah terbuang atau hilang dari layar, meniru perilaku Google Voice Typing native.
- **Peredam Chime Sistem Android Saat Restart Otomatis:**
  - Stream notifikasi dan sistem dibisukan selama sesi aktif berlangsung, dan stream media dibisukan sesaat saat restart agar bunyi chime/ding sistem Google tidak berulang kali mengganggu alur dikte.
  - Efek suara mekanikal WebAudio tetap terdengar normal.
- **Pemulihan Cerdas dengan Backoff Bertingkat (Resilient Recovery):**
  - Timeout hening biasa di-restart dengan jeda instan (40-60ms) tanpa jeda panjang.
  - Error engine atau koneksi ditangani dengan backoff adaptif (hingga 2.4s) guna mencegah loop restart yang tidak terkendali.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 87. CATATAN CHECKPOINT (v1.18.2 - Otomatisasi Penuh Always-On Google Voice Typing & Reduksi UI Clutter)
- **Otomatisasi Permanen Continuous Listening (Always-On Default):**
  - Mengunci status `aiSpeechAlwaysOn = true` secara permanen dan otomatis di klien web dan aplikasi APK.
  - Menghapus elemen checkbox manual "Always-On" (`#ai-alwayson-label`) dari antarmuka AI Workstation footer actions.
  - Bar aksi transkripsi kini lebih bersih dan ringkas: hanya menyisakan checklist `Auto-Send` berdampingan dengan tombol aksi `Undo`, `Clear`, dan `Send to Host`.
- **Perilaku Pengoperasian Alami:**
  - Mic langsung mendengarkan secara kontinu tanpa terpotong jeda berpikir, tanpa perlu mengaktifkan toggle tambahan.
  - Sesi dikte hanya berhenti saat pengguna secara eksplisit menekan tombol mikrofon utama untuk berhenti, berpindah mode kerja, atau mengirim teks.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons haptik tetap aktif sempurna di semua tombol.

---

## 88. CATATAN CHECKPOINT (v1.18.3 - Perbaikan Transkripsi Berulang & Stabilisasi Audio Mikrofon)
- **Eliminasi Bug Kata/Frasa Ditelan (Swallowed Repeated Speech):**
  - Menghapus aturan agresif `if (existCleanStr.includes(incCleanStr)) return existing;` dan dedup kata majemuk dari fungsi `mergeTranscripts()`.
  - Sebelumnya, jika pengguna mengulang kata atau kalimat uji coba seperti "cek satu dua dicoba", sistem salah mendeteksinya sebagai duplikat dan menolak menampilkannya ke layar.
  - Sekarang, kata atau kalimat berulang tersambung dengan aman dan utuh tanpa ada kata yang hilang.
- **Penyederhanaan Rangkaian Penggabungan Sesi (Clean Session Concatenation):**
  - `renderLiveTranscript()` dan `commitCurrentSession()` kini menggabungkan teks terakumulasi (`aiAccumulatedText`) dan teks sesi aktif secara langsung dengan spasi pemisah alami.
  - Hasil final Web Speech API di browser browser (`recognition.onresult`) langsung digabungkan dari array hasil resmi (`finalPieces.join(' ')`) dan interim (`interimPieces.join(' ')`) tanpa distorsi potongan silang.
- **Penstabilan Audio Stream Android APK:**
  - Menghapus pembungkaman audio stream native (`AudioManager.STREAM_NOTIFICATION`, `STREAM_SYSTEM`, `STREAM_MUSIC`) di `MainActivity.java` yang berpotensi mematikan suara klik mekanikal (`playClickSound()`) atau memicu `SecurityException: Not allowed by NotificationManager` pada Android 13+.
  - Menyesuaikan batas waktu pengenalan suara native Android (`EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS`: 1500ms, `COMPLETE_SILENCE`: 3500ms, `POSSIBLY_COMPLETE`: 2500ms) agar responsif dan tidak membekukan finalisasi kalimat pendek.
- **Kompilasi & Rilis APK:**
  - APK Android berhasil dikompilasi ulang dengan ukuran tetap ringan (5.4 MB) di `dist/DigiSmartDeck.apk` dan `static/DigiSmartDeck.apk`.
  - Versi aplikasi dan badge UI tersinkronisasi penuh ke `v1.18.3`.

---

## 89. CATATAN CHECKPOINT (v1.18.4 - Sinkronisasi UI APK dan Web Identik 100% & Redaman Nada Mic Google Voice)
- **Eliminasi Total Tombol Tambahan Khusus APK:**
  - Menghapus tombol `btn-bt` (Bluetooth HID) dan `btn-server-config` (Server IP) dari header Control Deck chips di `static/index.html`.
  - Menghapus logika inisialisasi bridge JS yang menampilkan tombol tersebut saat berjalan di APK WebView.
  - Tampilan antarmuka APK kini 100% IDENTIK dengan browser Chrome/Web tanpa ada satupun menu atau chip berbeda.
- **Pengembalian Redaman Nada Sistem (Silent Google Voice Recording):**
  - Mengaktifkan kembali mekanisme redaman stream audio sistem (`AudioManager.STREAM_NOTIFICATION`, `STREAM_SYSTEM`, dan redaman sementara `STREAM_MUSIC`) di `MainActivity.java`.
  - Saat mic mulai mendengarkan, saat restart berkala, serta saat rekaman dihentikan atau diputus, nada ding/chime sistem Google diredam secara senyap (silent) tanpa mengganggu alur dikte pengguna.
  - Sesi perekaman tetap berlangsung terus-menerus secara otomatis (Always-On Default).
- **Peredaman Total Bunyi Beep Penutup (Closing Chime Elimination):**
  - Memastikan `muteBeepStreams()` dipanggil secara konsisten dan tanpa syarat pada `stopNativeSpeech()`, `cancelNativeSpeech()`, `onEndOfSpeech()`, `onError()`, dan cabang akhir `onResults()`.
  - Pemulihan stream volume (`restoreBeepStreams`) ditunda selama 1000-1200ms saat rekaman selesai atau dibatalkan, sehingga bunyi nada penutup ('beep/ding' Google Speech) diredam 100% senyap tanpa suara sama sekali.
- **Kompilasi & Rilis APK Berpenamaan Versi (Versioned APK):**
  - File APK kini otomatis diberi nama sesuai versi SemVer rilis: `DigiSmartDeck-v1.18.4.apk` (5.4 MB).
  - Tersedia di `dist/DigiSmartDeck-v1.18.4.apk` dan `static/DigiSmartDeck-v1.18.4.apk` (serta `DigiSmartDeck.apk` untuk backward-compatibility).
  - Endpoint `/download/apk` di server otomatis menyajikan file dengan header download `attachment; filename="DigiSmartDeck-v1.18.4.apk"`.
  - Versi aplikasi tersinkronisasi ke `v1.18.4`.

---

## 90. CATATAN CHECKPOINT (v1.18.5 - Rilis Khusus Eliminasi Total Beep Penutup & Sinkronisasi Versi APK)
- **Eliminasi Total Beep Penutup saat Mic Berhenti:**
  - `stopNativeSpeech()`, `cancelNativeSpeech()`, dan `onEndOfSpeech()` di `MainActivity.java` langsung membisukan stream audio seketika sebelum Google SpeechRecognizer memicu sinyal stop.
  - Penundaan pemulihan volume (`restoreBeepStreams`) disetel ke 1200ms untuk menjamin proses penghentian rekaman berjalan 100% senyap tanpa ada nada ding/bloop penutup yang lolos.
- **Sinkronisasi Versi Otomatis (SemVer 2.0.0):**
  - Versi aplikasi resmi dinaikkan ke `v1.18.5`.
  - File instalasi berpenamaan versi baru telah dibuat: `DigiSmartDeck-v1.18.5.apk` (5.4 MB) di `dist/` dan `static/`.
  - Endpoint `/download/apk` menyajikan file `DigiSmartDeck-v1.18.5.apk` dengan status HTTP 200 OK.

---

## 91. CATATAN CHECKPOINT (v1.18.6 - Eliminasi Tombol Dev Header & Modernisasi Icon Refresh Windows PC)
- **Eliminasi Tombol Dev Bar Atas:**
  - Menghapus tombol fullscreen (`#btn-ai-fs`) dan tombol reload browser (`#btn-ai-reload`) dari header atas di `static/index.html`.
  - Menghapus event listener `_btnAiFs` dan `_btnAiReload` sehingga antarmuka header atas menjadi lebih bersih, rapi, dan terbebas dari tombol perkakas developer.
- **Modernisasi Icon Refresh Pembacaan Windows PC:**
  - Mengadopsi SVG modern panah reload melingkar (dari tombol reload sebelumnya) untuk menggantikan icon lama pada tombol refresh window switcher (`#btn-refresh-win-switcher`).
  - Fungsi tetap konsisten 100%: memindai dan menyegarkan daftar jendela aktif aplikasi/terminal di PC host (`openWindowSwitcherModal()`).
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi resmi dinaikkan ke `v1.18.6`.
  - File APK baru terkompilasi: `DigiSmartDeck-v1.18.6.apk` (5.4 MB) di `dist/DigiSmartDeck-v1.18.6.apk` dan `static/DigiSmartDeck-v1.18.6.apk`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan haptik tetap aktif sempurna di semua tombol interaktif.

---

## 92. CATATAN CHECKPOINT (v1.19.0 - Penambahan Mode Power & Kontrol Sesi Multi-OS)
- **Penambahan Mode Power (Mode ke-4 Utama):**
  - Menjadikan DigiSmartDeck memiliki 4 mode sentral: Keyboard PC, Game Controller, AI Workstation, dan Power Control.
  - Menambahkan tombol quick mode `#quick-mode-power` di header atas sejajar dengan mode lainnya.
  - Menambahkan chip `#btn-power-mode` di menu Control Deck.
  - Menghadirkan antarmuka `#power-view` yang elegan, imersif, dan touch-friendly di orientasi landscape.
- **Dukungan Perintah Daya & Sesi Adaptif Multi-OS:**
  - Menyesuaikan label dan mekanisme perintah kernel sesuai sistem operasi host (`ubuntu`, `win`, `mac`).
  - **Shutdown:** `systemctl poweroff` (Linux), `shutdown /s /t 0` (Windows), `osascript shut down` (macOS).
  - **Restart:** `systemctl reboot` (Linux), `shutdown /r /t 0` (Windows), `osascript restart` (macOS).
  - **Sleep / Suspend:** Menampilkan "Suspend" di Linux (`systemctl suspend`), "Sleep" di Windows (`rundll32 powrprof.dll`), "Sleep" di macOS (`pmset sleepnow`).
  - **Lock Screen:** "Lock Session" di Linux (`loginctl lock-session` / screensaver), "Lock Workstation" di Windows (`user32.dll LockWorkStation`), "Lock Screen" di macOS (`pmset displaysleepnow`).
  - **Switch User:** "Switch User (Greeter)" di Linux (`dm-tool switch-to-greeter` / gdbus), "Switch User (tsdiscon)" di Windows, "Fast User Switching" di macOS (`CGSession`).
  - **Sign Out / Logout:** Keluar sesi aktif di Linux (`gnome-session-quit`), Windows (`shutdown /l`), dan macOS (`osascript log out`).
  - **Turn Off Screen:** Mematikan layar display tanpa menidurkan PC (`xset dpms force off` di Linux, PowerShell SendMessage di Windows).
  - **Hibernate:** Simpan memori RAM ke disk dan matikan PC.
- **Proteksi Konfirmasi Keselamatan (Safety Confirmation):**
  - Modal konfirmasi `#modal-power-confirm` melindungi aksi berbahaya (Shutdown, Restart, Sign Out) dari sentuhan tidak sengaja di layar ponsel.
  - Aksi instan (Kunci Layar, Matikan Monitor, Sleep, Switch User) dieksekusi seketika demi kenyamanan pengguna.
- **Integrasi Backend Server & API:**
  - WebSocket mendukung pesan `type: 'power_action'` dengan feedback instan `type: 'power_result'`.
  - Endpoint REST API `/api/power` (GET & POST) ditambahkan untuk fleksibilitas kontrol eksternal.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi resmi aplikasi dinaikkan ke `v1.19.0` (minor bump fitur baru).
  - File instalasi APK baru terkompilasi: `DigiSmartDeck-v1.19.0.apk` (5.4 MB) di `dist/` dan `static/`.
  - Endpoint `/download/apk` menyajikan `DigiSmartDeck-v1.19.0.apk`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
## 93. CATATAN CHECKPOINT (v1.20.0 - Sistem Auto-Update In-App OTA & Integrasi FileProvider Installer APK)
- **Arsitektur Auto-Update OTA In-App Mandiri (Self-Updating APK):**
  - Mengeliminasi kebutuhan unduh manual via browser dan pencarian file APK di folder download HP.
  - Mempersiapkan transisi pemadaman versi web seluler menuju APK Android mandiri yang memperbarui dirinya sendiri dalam 1 ketukan.
- **Konfigurasi Izin & FileProvider Android:**
  - Menambahkan izin `android.permission.REQUEST_INSTALL_PACKAGES` pada `AndroidManifest.xml`.
  - Mengonfigurasi `androidx.core.content.FileProvider` dengan otoritas `${applicationId}.fileprovider` yang merujuk pada `file_paths.xml`.
  - Mendukung direktori cache dan file aplikasi eksternal maupun internal secara aman untuk pertukaran intent installer ke sistem operasi Android.
- **Integrasi Native Java Bridge (`MainActivity.java`):**
  - Menambahkan method bridge `@JavascriptInterface`: `isNativeApp()`, `getInstalledVersionName()`, `getInstalledVersionCode()`, dan `downloadAndInstallUpdate(downloadUrl, targetVersion)`.
  - Mengimplementasikan background download stream berbasis `ExecutorService` dan `HttpURLConnection` yang mengirim event progres berkala ke UI WebView (`window.onUpdateDownloadProgress`).
  - Menangani izin instalasi sumber tidak dikenal (`ACTION_MANAGE_UNKNOWN_APP_SOURCES`) pada Android 8.0+ dan meluncurkan dialog instalasi sistem (`Intent.ACTION_VIEW` dengan MIME `application/vnd.android.package-archive` dan `FLAG_GRANT_READ_URI_PERMISSION`).
- **Endpoint Backend Server (`server.py`):**
  - Menambahkan endpoint REST API `/api/updater/check` yang membaca versi server terkini, `version_code`, ukuran file APK, URL unduhan, dan status `update_available` berdasarkan versi klien yang memanggil.
  - Endpoint `/download/apk` dan `/DigiSmartDeck.apk` kini melayani file rilis APK Android terbaru secara dinamis dari `static/` atau `dist/`.
- **Antarmuka Pengguna & Indikator Progres (`static/index.html`):**
  - Modal About menampilkan badge platform `APK Native` saat dijalankan dari aplikasi Android resmi.
  - Tombol pembaruan otomatis menyesuaikan teks dan ukuran file (`Pasang Pembaruan Sekarang (6.3 MB)`).
  - Menampilkan progress bar dan persentase unduhan real-time saat proses pengunduhan paket APK berlangsung.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap terjaga.
  - Ukuran file APK tetap sangat ringan (~6.3 MB, jauh di bawah batas 20 MB).

---

## 94. CATATAN CHECKPOINT (v1.20.1 - Kode Akses Developer richdaddycompany & Endpoint Pairing REST)
- **Kode Akses Pengembang Mandiri (richdaddycompany):**
  - Mengimplementasikan bypass master code `richdaddycompany` (case-insensitive) pada `DevicePairingManager` di `auth_manager.py`.
  - Melewati proteksi lockout, PIN TTL, dan pembatasan input numeric 6-digit.
  - Menghasilkan token developer permanen (`dev_rdc_*`) yang diotorisasi secara instan tanpa perlu melihat monitor PC.
  - Mendukung kunci lisensi `RICHDADDYCOMPANY` di `LicenseManager` untuk akses seumur hidup (Lifetime Pro).
- **Fleksibilitas Input Antarmuka (static/index.html):**
  - Menambahkan menu/input 'Gunakan Kode Akses Dev (richdaddycompany)' pada modal pairing (`#modal-pairing`).
  - Menangani paste teks berkarakter huruf di kotak PIN agar langsung memicu verifikasi kode dev.
  - Menyediakan fallback sinkronisasi pairing via REST API `/api/pair` jika WebSocket mengalami penundaan.
- **Endpoint HTTP REST /api/pair (server.py):**
  - Menerima POST/GET request dengan parameter `pin` dan `device_name` untuk pairing cepat.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.1`.
  - File APK baru terkompilasi di `dist/` dan `static/`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 95. CATATAN CHECKPOINT (v1.20.2 - Eliminasi Pemblokiran navigator.onLine & Stabilitas Koneksi Wi-Fi LAN)
- **Eliminasi Pemblokiran Jaringan Lokal (navigator.onLine):**
  - Menghapus pengecekan `navigator.onLine` pada `connect()`, `handleDisconnect()`, dan `scheduleReconnect()` di `static/index.html`.
  - Pada jaringan lokal offline, air-gapped, maupun Wi-Fi internal tanpa akses internet WAN, browser Android WebView kerap menetapkan `navigator.onLine = false` sehingga koneksi WebSocket ke host PC sebelumnya sempat terblokir dan menampilkan label keliru 'Wi-Fi Terputus'.
  - Memperbaiki event listener `offline` dan `online` agar tidak mematikan paksa WebSocket lokal yang masih aktif terhubung.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.2`.
  - File APK baru terkompilasi di `dist/` dan `static/`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 96. CATATAN CHECKPOINT (v1.20.3 - Dukungan PIN Dev 888888 & Pemulihan Tombol Mode Control Deck)
- **Integrasi Master PIN Developer 888888 & 8888:**
  - Menambahkan dukungan PIN `888888` dan `8888` pada `DevicePairingManager.verify_and_register` di `auth_manager.py`.
  - PIN developer terhubung dengan kode aktivasi master `richdaddycompany` dan otomatis mengaktifkan lisensi Lifetime Pro Developer (`RICHDADDYCOMPANY`) pada `LicenseManager`.
  - Memperbarui `submitPairingPin()` di `static/index.html` agar menerima input developer tanpa terblokir validasi PIN reguler.
  - Menambahkan tombol instan 'Aktifkan Akses Dev (PIN: 888888)' pada modal pairing untuk auto-fill dan aktivasi developer 1-ketukan.
- **Pemulihan Sentral Tombol Mode Kerja (Control Deck & Header):**
  - Menambahkan kembali Section 0: Mode Kerja Utama pada antarmuka `#control-deck` dengan 4 mode lengkap: Keyboard PC (`#btn-mode-standard`), Game Controller (`#btn-game-mode`), AI Workstation (`#btn-ai-mode`), dan Power Menu (`#btn-power-mode`).
  - Memperbesar area sentuh tombol mode header (`.header-mode-btn`) menjadi 32x32px dengan `touch-action: manipulation` agar responsif terhadap sentuhan jari di layar sentuh ponsel.
  - Mengoptimalkan helper `bindModeBtn()` dengan mekanisme debounce 250ms dan penanganan event touch/click yang bersih agar tidak terjadi pembatalan klik atau pemanggilan ganda.
  - Memperbaiki penanganan `activeOs` pada `switchAppMode('power')` agar kebal terhadap status uninitialized variabel OS.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.3`.
  - File APK baru terkompilasi di `dist/` dan `static/`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 97. CATATAN CHECKPOINT (v1.20.4 - Pemulihan Tombol Wi-Fi & Mode Scan Koneksi Subnet)
- **Pemulihan Interaksi Tombol Badge Wi-Fi:**
  - Menghapus blokir `if (!connected)` pada event badge status Wi-Fi `#badge`.
  - Tapping atau clicking badge Wi-Fi di layar ponsel kini selalu membuka modal Host Discovery & Subnet Scanner (`#modal-reconnect`) secara instan baik dalam kondisi terhubung maupun terputus.
  - Menambahkan event listener `touchend` dengan `e.preventDefault()` untuk menjamin responsivitas sentuhan di Android WebView.
  - Modal Reconnect kini menampilkan status host terkini secara real-time (`[Terhubung]` atau `[Terputus]`).
- **Aktivasi Tombol Pindai Jaringan pada Reconnect Banner:**
  - Menambahkan tombol aksi 'Pindai Jaringan (Scan IP)' (`#btn-rc-scan`) dan 'Coba Lagi' (`#btn-rc-retry`) secara visual di dalam antarmuka `#reconnect-banner`.
  - Saat koneksi Wi-Fi terputus, banner modal otomatis tampil dan pengguna dapat langsung menekan tombol 'Pindai Jaringan' untuk mendeteksi IP baru host PC server di subnet lokal.
  - Memperbaiki event listener `offline` dan `online` agar seketika mendeteksi pemutusan jaringan dan meluncurkan proses pemulihan serta mode pemindaian.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.4`.
  - File APK baru terkompilasi di `dist/` dan `static/`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 98. CATATAN CHECKPOINT (v1.20.5 - Aktivasi Mandiri & Otomatis Sistem Auto-Updater OTA)
- **Sistem Auto-Updater Otomatis & Terjadwal (static/index.html):**
  - Mengimplementasikan alur pemeriksaan pembaruan OTA otomatis di latar belakang via fungsi `checkAutoUpdate(silent = true)`.
  - Terpicu mandiri tanpa interaksi manual pada beberapa titik utama:
    1. 2.5 detik setelah aplikasi dibuka (startup / splash screen).
    2. Seketika saat WebSocket berhasil terhubung ke host PC (`ws.onopen`).
    3. Berkala setiap 15 menit melalui timer interval background.
    4. Saat pesan inisialisasi WebSocket (`init`) mendeteksi versi server lebih tinggi dari versi klien.
- **Banner Notifikasi Pembaruan Melayang (Floating Notification Banner):**
  - Menambahkan `#update-notification-banner` dengan tampilan sleek cyber dark-mode di sudut atas antarmuka.
  - Menampilkan ringkasan versi baru, ukuran file APK, tombol aksi 1-ketukan 'Pasang', 'Detail', dan 'Tutup'.
  - Dilengkapi progress bar unduhan real-time inline di dalam banner saat proses download berlangsung via `DigiAndroidBridge.downloadAndInstallUpdate()`.
  - Menambahkan indikator dot badge berdenyut (`#update-badge-dot`) pada tombol About di header saat update tersedia.
- **Helper Toast Terpadu (showSmartToast):**
  - Mengimplementasikan fungsi global `showSmartToast(msg, app)` yang terhubung langsung ke `#smart-context-toast` sehingga seluruh panggilan toast status berjalan mulus tanpa error.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.5`.
  - Sinkronisasi konstanta `APP_CLIENT_VERSION` dan `APP_CLIENT_VERSION_CODE` pada `bump-version.sh`.
  - File APK baru terkompilasi di `dist/` dan `static/`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 99. CATATAN CHECKPOINT (v1.20.6 - Pemulihan Deklarasi isPowerModeActive & Responsivitas Ikon Top Bar)
- **Akar Masalah Malfungsi Ikon Top Bar (Root Cause):**
  - Pada penambahan Power Mode sebelumnya, variabel global `isPowerModeActive` lupa dideklarasikan di level scope atas IIFE JavaScript.
  - Akibat mode strict (`'use strict'`), pemanggilan `switchAppMode('standard')` pada saat startup memicu exception fatal: `ReferenceError: isPowerModeActive is not defined`.
  - Exception ini menghentikan eksekusi script JavaScript tepat sebelum baris binding listener ikon-ikon mode header (`quick-mode-*`), chip context switcher (`smart-context-chip`), dan sinkronisasi inisialisasi lainnya.
  - Tombol menu `#btn-control-deck` tetap berfungsi karena listener-nya terpasang sebelum titik exception tersebut.
- **Perbaikan & Optimalisasi Sentral:**
  - Mendeklarasikan `let isPowerModeActive = false;` pada Work Mode Global States di `static/index.html`.
  - Mengimplementasikan `dismissSplashScreenNow()` agar interaksi pengguna pada tombol top bar seketika menutup splash screen dan langsung membuka modal yang dituju tanpa terblokir status transisi.
  - Menambahkan listener sentuh instan `touchend` dengan debounce pada `#btn-brand-toggle` (About) dan `#smart-context-chip` (Window Switcher) agar sangat responsif terhadap sentuhan jari di layar sentuh mobile.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.6`.
  - File APK baru terkompilasi di `dist/` dan `static/`.
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 100. CATATAN CHECKPOINT (v1.20.7 - Pengaturan Kecerahan Layar, Volume Suara, Wake Up, Anti-Sleep pada Power Mode & Eliminasi Section Mode Utama)
- **Eliminasi Menu Mode Kerja Utama pada Control Deck (static/index.html):**
  - Menghapus Section 0 (`MODE KERJA UTAMA`) dari slide-out `#control-deck`.
  - Perpindahan mode kerja kini terpusat dan efisien langsung melalui deretan tombol header di top bar (`#header-modes`).
- **Restrukturisasi Header Power Mode (#power-view):**
  - Menghapus tombol pintasan keyboard `#btn-power-back` sesuai instruksi pengguna.
  - Memindahkan badge nama sistem operasi dan hostname host (`#power-os-badge`) ke pojok kanan atas header (`.power-header-right`).
  - Menempatkan judul menu secara elegan di sisi kiri header (`.power-header-left`).
- **Integrasi Panel Kontrol Sistem Modern (static/index.html & server.py):**
  - **Pengaturan Kecerahan Layar (Display Brightness):**
    - Tombol penyesuaian bertahap -10% dan +10%, slider rentang halus 10% - 100%, serta preset cepat (30%, 50%, 75%, 100%).
    - Backend terintegrasi multi-layer: `xrandr` untuk monitor eksternal X11, `brightnessctl` untuk panel laptop, WMI PowerShell untuk Windows, dan osascript untuk macOS.
  - **Pengaturan Volume Suara (Audio Volume):**
    - Tombol Mute toggle instan, tombol -5% dan +5%, slider rentang 0% - 100%, serta preset cepat (0%, 30%, 60%, 80%, 100%).
    - Backend terhubung langsung ke PipeWire/PulseAudio (`pactl set-sink-volume`), `set_system_volume()`, dan fallback pynput/uinput key events.
  - **Fitur Bangunkan Layar / PC (Wake Up):**
    - Tombol aksi 1-ketukan untuk membangunkan layar dari kondisi redup/blanking (`xset dpms force on; xdg-screensaver reset`, simulasi pergerakan kursor mouse/shift key).
  - **Fitur Tetap Terjaga / Anti-Sleep (Supaya PC Tidak Sleep):**
    - Sakelar toggle ("Tetap Terjaga") yang mengaktifkan mode caffeine.
    - Menonaktifkan DPMS monitor timeout (`xset -dpms; xset s off; xset s noblank`), mengaktifkan `systemd-inhibit` background idle/sleep lock, serta watchdog heartbeat berkala tiap 30 detik.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.7`.
  - File APK baru terkompilasi di `dist/` dan `static/` (5.4 MB).
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.

---

## 101. CATATAN CHECKPOINT (v1.20.8 - Optimasi Responsif Tampilan HP Mobile: Power Mode Landscape Compact, Perbaikan Potret, dan Pemisahan Keyboard)
- **Optimasi Landscape Ponsel (Tampilan Mendatar):**
  - Menerapkan query media ultra-kompak `@media (max-height: 520px) and (orientation: landscape)` untuk `.power-view`.
  - Mengurangi padding, ukuran kartu kontrol (~60px), slider, dan kartu aksi daya sehingga seluruh 3 panel kontrol dan 8 tombol aksi daya muat 100% di layar ponsel tanpa memerlukan scrolling vertikal (tinggi total ~260px, aman di rentang 360px-412px tinggi ponsel).
  - Merestrukturisasi kartu Volume Suara dengan memindahkan chip tombol Mute ke baris header kanan di samping badge persentase volume, menyelaraskan bentuk tata letak secara simetris dengan kartu Kecerahan Layar.
- **Perbaikan Isolasi Tampilan Potret & Penanganan Keyboard (.kb-wrap):**
  - Memperbaiki bug di mana selector potret `.kb-wrap` memiliki `display: flex !important;` tanpa filter class `.hidden`, yang menyebabkan keyboard tetap tampil menumpuk di atas tampilan mode khusus saat dibuka dalam mode vertikal.
  - Menambahkan aturan `.kb-wrap.hidden { display: none !important; }` dan `.laptop-deck.hidden { display: none !important; }`, serta memperbarui `switchAppMode` untuk secara eksplisit mengelola class `.hidden` pada `.kb-wrap`.
  - Pada layar ponsel potret yang sempit (lebar <= 480px), indikator ping dan context chip di-hide dari top bar untuk mencegah tumpang-tindih visual dengan logo.
- **Akses Fleksibel pada Guard Orientasi (#orientation-landscape-guard):**
  - Menambahkan tombol kedua "Lanjutkan dalam Mode Vertikal" (`#btn-continue-portrait`) pada modal pengingat orientasi sehingga pengguna tidak terkunci apabila sistem auto-rotate ponsel sedang dinonaktifkan.
  - Menambahkan kelas `portrait-dismissed` pada `body` saat tombol ditekan dengan feedback klik suara mekanikal (`playClickSound()`) dan getaran haptik (`vibe(15)`).
  - Menyinkronkan kunci kamus multibahasa `guard_continue_portrait` pada `I18N.en` dan `I18N.id`.
- **Kompilasi & Rilis APK Berpenamaan Versi (SemVer 2.0.0):**
  - Versi aplikasi dinaikkan ke `v1.20.8`.
  - File APK baru terkompilasi di `dist/` dan `static/` (~5.4 MB).
  - Layanan `digikeyboard.service` di-refresh.
- **Kepatuhan Aturan Mutlak:**
  - STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, dan teks respons asisten.
  - Efek suara klik mekanikal (`playClickSound()`) dan respons getar haptik tetap aktif sempurna.


