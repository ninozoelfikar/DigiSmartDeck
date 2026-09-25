# ⌨️ Remote PC Keyboard (KDE Connect Alternative - Khusus Input Keyboard Standar PC)

Aplikasi remote keyboard nirkabel untuk mengontrol PC/Laptop melalui layar HP atau Tablet via jaringan Wi-Fi lokal.

Dibuat khusus agar **menampilkan layout keyboard fisik standar PC** di layar sentuh perangkat bergerak, **tanpa memunculkan keyboard bawaan HP (Gboard/SwiftKey/dsb.)**, sehingga Anda mendapatkan akses langsung ke seluruh tombol fungsi PC seperti **Shift, Tab, Esc, Ctrl, Alt, Win/Super, Enter, Backspace, Arrows**, baris angka/simbol, hingga **F1-F12** dan **Numpad**.

---

## ✨ Fitur Utama

1. **Layout Keyboard Fisik Standar PC di Layar:**
   - **Row 1:** Baris Angka lengkap (`1` s/d `0`, `-`, `=`) dan simbol Shift (`!`, `@`, `#`, `$`, `%`, `^`, `&`, `*`, `(`, `)`, `_`, `+`) + tombol **Backspace** lebar.
   - **Row 2:** Tombol **Tab ⇥**, baris **QWERTY**, tanda kurung siku `[ {`, `] }`, dan `\ |`.
   - **Row 3:** Tombol **Caps Lock ⇪**, baris **ASDFGHJKL**, tanda baca `; :`, `' "`, dan tombol **Enter ↵** lebar.
   - **Row 4:** Tombol **Shift ⇧ (Kiri & Kanan)**, baris **ZXCVBNM**, `, <`, `. >`, `/ ?`, dan tombol panah **▲**.
   - **Row 5:** Tombol **Ctrl**, **Win ⊞ (Super)**, **Alt**, **Space Bar** panjang, serta tombol panah **◀ ▼ ▶**.

2. **Panel Tambahan Fleksibel (Bisa di-toggle kapan saja):**
   - **Fn Bar:** Tombol `Esc`, `F1` sampai `F12`.
   - **Nav Bar:** Tombol navigasi PC seperti `Insert`, `Delete`, `Home`, `End`, `Page Up`, `Page Down`, `Print Screen`.
   - **PC Numpad:** Blok angka kalkulator PC (17 tombol) dengan `NumLock`, `/`, `*`, `-`, `+`, `Enter`.
   - **Shortcut Cepat:** Tombol sekali tekan untuk kombinasi populer: `Ctrl+C`, `Ctrl+V`, `Ctrl+Z`, `Ctrl+A`, `Alt+Tab`, `Win+D`, `Ctrl+Alt+Del`.

3. **Mekanisme Khusus Layar Sentuh:**
   - **Latch / Sticky Modifier Mode:** Tekan tombol `Ctrl`, `Alt`, atau `Shift` satu kali untuk menguncinya, lalu tekan tombol huruf (misal `C` untuk copy), modifier akan otomatis melepas dirinya sendiri setelah huruf terkirim. Anda juga bisa menonaktifkan mode ini untuk pure multi-touch.
   - **Multi-Touch Nyata:** Mendukung penekanan beberapa tombol sekaligus dengan multi-jari.
   - **Haptic Feedback:** Getaran lembut saat tombol fisik virtual ditekan (bisa dinyalakan/dimatikan dengan tombol `📳`).
   - **Bebas Keyboard Virtual HP:** Tidak ada field teks tersembunyi yang memicu keyboard bawaan Android/iOS muncul menutupi layar.

4. **Koneksi Super Cepat & Ringan:**
   - Menggunakan protokol **WebSocket** via Wi-Fi lokal dengan latensi ultra rendah (1-5 ms).
   - Indikator koneksi langsung dan ping latency monitor.
   - Cukup scan **QR Code** di terminal PC dengan kamera HP atau buka tautan IP di browser HP.

---

## 🚀 Cara Menjalankan

### Persyaratan:
- Komputer dan HP/Tablet terhubung ke **jaringan Wi-Fi yang sama**.
- Python 3.8+ terinstal di PC.

### Di Linux / macOS:
```bash
cd remote-pc-keyboard
./run.sh
```
*(Atau jalankan manual: `python3 -m pip install -r requirements.txt && python3 server.py`)*

> **Catatan Linux:** Pastikan display server X11 aktif (default pada sebagian besar distro desktop). Jika menggunakan X11, `pynput` langsung dapat mengendalikan keyboard.

### Di Windows:
Cukup klik ganda (double-click) berkas:
```
run.bat
```
*(Atau buka Command Prompt / PowerShell lalu ketik `python server.py`)*

---

## 📱 Cara Menghubungkan HP / Tablet

1. Setelah server berjalan di PC, terminal akan menampilkan alamat URL lokal dan **QR Code**, contoh:
   ```
   http://192.168.1.15:8080
   ```
2. Di HP Anda:
   - Arahkan kamera HP ke QR Code yang muncul di terminal PC, ATAU
   - Buka browser (Chrome / Safari / Firefox) di HP dan ketik alamat IP yang tertera.
3. Tampilan keyboard standar PC akan langsung terbuka di browser HP.
4. **Tips Penggunaan Terbaik:**
   - Putar HP ke posisi **Lanskap (Landscape / Miring)**.
   - Tekan tombol **⛶ (Fullscreen)** di pojok kanan atas untuk pengalaman layar penuh tanpa gangguan bar browser.

---

## 📁 Struktur Direktori

```
remote-pc-keyboard/
├── server.py              # Server WebSocket + HTTP + deteksi IP & QR Code
├── requirements.txt       # Dependencies (aiohttp, pynput, qrcode)
├── run.sh                 # Script instan untuk Linux / macOS
├── run.bat                # Script instan untuk Windows
├── static/
│   ├── index.html         # Antarmuka keyboard PC standar
│   ├── style.css          # Desain tombol mekanik PC & responsif mobile
│   └── app.js             # Logika sentuh, multi-touch, latch, dan websocket
└── README.md              # Dokumentasi lengkap
```
