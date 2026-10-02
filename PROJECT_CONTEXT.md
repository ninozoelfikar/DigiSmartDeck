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
    - Header atas tombol branding (`#btn-brand-toggle`): tooltip title "About DigiKeyboard - King Ali Studiō" (EN) / "Tentang DigiKeyboard - King Ali Studiō" (ID).
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
  - Mengetuk jendela pilihan akan memicu bunyi klik mekanikal (`playClickSound()`), getaran haptik (`vibe(20)`), menutup popover, mengirim perintah aktivasi & pemaksimalan ke PC, serta langsung mengubah mode DigiKeyboard di ponsel agar sesuai dengan aplikasi tersebut (misal Terminal/VS Code langsung masuk ke AI Workstation).
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
