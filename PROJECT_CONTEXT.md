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











