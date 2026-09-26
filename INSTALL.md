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
