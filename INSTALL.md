# 📦 Panduan Instalasi & Penggunaan Multi-Platform

DigiKeyboard dirancang untuk bekerja secara mulus di berbagai sistem operasi:
- **Host Server (PC yang dikendalikan):** Windows, Linux, macOS
- **Client (HP/Tablet/Browser pengendali):** Android, iOS (iPhone & iPad), Windows, Mac, Linux

---

## 🖥️ Menjalankan Server di PC / Laptop

### 1. Windows (10 / 11)
1. Pastikan **Python 3.8+** sudah terinstal (unduh di [python.org](https://www.python.org/)).
   > *PENTING: Pastikan centang opsi **"Add Python to PATH"** saat instalasi.*
2. Buka folder `digikeyboard`, lalu **klik ganda (double-click)**:
   ```cmd
   run.bat
   ```
   *Skrip ini otomatis mendeteksi launcher Python (`python` atau `py`), menginstal dependensi (`aiohttp`, `pynput`, `qrcode`), dan langsung menjalankan server.*
3. Catat alamat IP lokal atau scan QR Code yang muncul di terminal.

### 2. Linux (Ubuntu, Debian, Fedora, Arch)
1. Buka terminal di folder project:
   ```bash
   cd digikeyboard
   ```
2. **Direkomendasikan (Dukungan Layar Login, Lock Screen & Password):**
   ```bash
   chmod +x setup-uinput.sh
   ./setup-uinput.sh
   ```
   *Mengaktifkan modul kernel Linux `uinput` sehingga DigiKeyboard bertindak sebagai keyboard USB fisik.*
3. **Atau jalankan langsung melalui runner:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

### 3. macOS (Apple Silicon / Intel)
1. Buka Terminal di folder project:
   ```bash
   cd digikeyboard
   chmod +x run.sh
   ./run.sh
   ```
2. **Izin Aksesibilitas (Wajib di macOS):**
   macOS mewajibkan izin Accessibility agar aplikasi dapat mengirim input keyboard & mouse:
   - Buka **System Settings** > **Privacy & Security** > **Accessibility**.
   - Tambahkan dan aktifkan **Terminal** atau **iTerm**.

---

## 📱 Menggunakan di HP / Tablet (Client)

### 1. Android (Google Chrome, Samsung Internet, Edge, Firefox)
1. Hubungkan HP ke **jaringan Wi-Fi yang sama** dengan PC.
2. Buka browser dan buka alamat IP PC Anda (misal `http://192.168.8.103:8080`), atau scan QR Code di terminal.
3. Putar HP ke posisi **Landscape (Mendatar)**.
4. **Tips Fullscreen / PWA:**
   - Ketuk menu titik tiga di browser > pilih **"Add to Home screen" / "Instal Aplikasi"**.
   - DigiKeyboard akan terbuka dalam layar penuh tanpa toolbar browser!

### 2. iOS (iPhone & iPad - Safari)
1. Hubungkan iPhone/iPad ke **Wi-Fi yang sama** dengan PC.
2. Buka **Safari** dan ketik alamat IP server.
3. **Tips Fullscreen di iOS (Sangat Direkomendasikan):**
   - Ketuk tombol **Share (Bagikan)** di Safari (ikon kotak dengan panah atas).
   - Pilih **"Add to Home Screen" (Tambahkan ke Layar Utama)**.
   - Buka ikon DigiKeyboard dari Home Screen Anda.
   - DigiKeyboard akan berjalan dalam mode **Standalone Fullscreen** dengan dukungan safe-area notch iPhone dan home bar!

---

## 🔥 Firewall (Jika Client Tidak Bisa Membuka Halaman Web)

- **Ubuntu / Debian:**
  ```bash
  sudo ufw allow 8080/tcp
  ```
- **Fedora / RHEL:**
  ```bash
  sudo firewall-cmd --add-port=8080/tcp --permanent && sudo firewall-cmd --reload
  ```
- **Windows:**
  Jika muncul pop-up *Windows Defender Firewall*, centang **Private Networks** lalu klik **Allow access**.
- **macOS:**
  Jika firewall aktif, buka *System Settings > Network > Firewall* dan izinkan koneksi masuk untuk Python.

---

## 📦 Build Standalone Executable (Tanpa Python di PC Target)

Jika Anda ingin mendistribusikan aplikasi sebagai satu file aplikasi mandiri:

### 1. Windows (`.exe`)
Jalankan file batch:
```cmd
build-exe.bat
```
Hasil: `dist\DigiKeyboard.exe` (Standalone Windows Executable dengan icon).

### 2. Linux (Binary Executable)
Jalankan script bash:
```bash
chmod +x build-linux.sh
./build-linux.sh
```
Hasil: `dist/DigiKeyboard` (Standalone ELF Binary). Jalankan langsung dengan `./dist/DigiKeyboard`.

### 3. macOS (`.app` Bundle & Binary)
Jalankan script bash di macOS:
```bash
chmod +x build-macos.sh
./build-macos.sh
```
Hasil:
- Terminal Binary: `dist/DigiKeyboard`
- macOS Application Bundle: `dist/DigiKeyboardApp.app`

---

## 📱 Build & Penggunaan Android Native APK (Solusi Bebas Pop-up Chrome & Bluetooth HID)

Untuk pengalaman terbaik di HP/Tablet Android tanpa pop-up keamanan Chrome (*"Swipe down to exit fullscreen"*), tanpa bilah alamat browser, dan dengan opsi **Bluetooth HID**, gunakan aplikasi **DigiKeyboard APK**.

### 1. Cara Download Langsung dari HP (Paling Cepat):
1. Jalankan server DigiKeyboard di PC.
2. Buka browser di HP ke alamat:
   ```text
   http://<PC_IP>:8080/download/apk
   ```
   Atau buka `http://<PC_IP>:8080` dan klik tombol **"📱 Download Android APK"** di header atas.
3. Pasang file `DigiKeyboard.apk` di HP Android Anda.

### 2. Fitur Spesial Android APK:
- **True Immersive Sticky Fullscreen:** 100% bebas dari pop-up peringatan Chrome.
- **Koneksi Wi-Fi Fleksibel:** Masukkan alamat IP server PC langsung di dalam aplikasi saat pertama kali dibuka.
- **Mode Bluetooth HID Hardware Emulation:**
  - Mendukung emulasi hardware Keyboard + Mouse Bluetooth standar via `BluetoothHidDevice` (Android 9+).
  - Sambungkan (pair) Bluetooth ponsel Anda langsung ke PC, Mac, iPad, Android TV, atau Smart TV.
  - Berfungsi tanpa perlu menginstal aplikasi server apa pun di PC target!

### 3. Cara Build APK Sendiri dari Source Code:
1. **Menggunakan Script CLI (Otomatis):**
   ```bash
   ./build-apk.sh
   ```
   Hasil APK siap pakai akan otomatis disimpan di `dist/DigiKeyboard.apk` dan `static/DigiKeyboard.apk`.
2. **Menggunakan Android Studio:**
   - Buka Android Studio > pilih **Open** > arahkan ke folder `android/`.
   - Pilih menu **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
3. **Build Otomatis Cloud via GitHub Actions:**
   - Cukup push project ke GitHub. Workflow `.github/workflows/build-apk.yml` akan otomatis mengompilasi APK dan menyediakannya untuk di-download langsung di tab **Actions > Artifacts**.

---

## 🛡️ Fitur Anti-Tabrakan Pengendali (Multi-Device Arbitration)

Jika Anda memiliki beberapa HP atau tablet yang membuka DigiKeyboard secara bersamaan:
1. **Pengendali Aktif (`🟢 👑`):** Perangkat pertama yang tersambung menjadi pengendali utama yang dapat mengetik dan menggerakkan mouse.
2. **Mode Siaga (`🟡 ⚡`):** Perangkat kedua dan seterusnya otomatis berstatus siaga. Tombol yang diketik tidak akan dikirimkan ke PC untuk mencegah teks bertabrakan atau kursor mouse bergerak liar.
3. **Ambil Alih Kendali (Takeover):**
   - **Manual:** Ketuk tombol status `🟡 ⚡ Siaga` di layar HP Anda, lalu konfirmasi **"Ya, Ambil Alih"**. Kendali langsung berpindah ke HP Anda.
   - **Otomatis (Idle Timeout):** Jika pengendali aktif tidak melakukan pengetikan selama 30 detik, perangkat siaga yang mengetik tombol akan otomatis mengambil alih kendali.

---

## 🛠️ Pemeriksa Sistem Otomatis (System Pre-Flight Checker)

Saat Anda menjalankan server:
- Skrip [`system_checker.py`](system_checker.py) akan memverifikasi kesehatan jaringan lokal, ketersediaan port 8080, status firewall, dan hak akses Linux `/dev/uinput`.
- Jika port 8080 sudah digunakan oleh daemon DigiKeyboard lain, aplikasi mendeteksinya secara cerdas dan menampilkan URL aktif tanpa error crash atau traceback.


