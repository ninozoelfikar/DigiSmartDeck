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



