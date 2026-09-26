# 📦 Cara Install & Jalankan di Linux PC

## Prasyarat
- PC/Laptop Linux (Ubuntu / Debian / Fedora / Arch)
- HP/Tablet berada di **jaringan WiFi yang sama** dengan PC
- Sesi **Desktop GUI** aktif (bukan pure SSH tanpa X11)

---

## ⚡ Cara Tercepat (1 Perintah)

```bash
# 1. Clone project ke PC
git clone https://github.com/ninozoelfikar/digikeyboard.git
cd digikeyboard

# 2. Jalankan installer otomatis
chmod +x install-linux.sh
./install-linux.sh
```

Script `install-linux.sh` akan otomatis:
- ✅ Memeriksa & menginstal Python 3 (jika belum ada)
- ✅ Menginstal semua dependencies (`aiohttp`, `pynput`, `qrcode`)
- ✅ Memeriksa koneksi keyboard ke display X11/Wayland
- ✅ Mendeteksi IP lokal PC
- ✅ Menampilkan petunjuk buka firewall jika diperlukan
- ✅ Menampilkan URL + QR Code langsung di terminal

---

## 🔧 Cara Manual (Jika Prefer)

```bash
# Install dependencies
pip install aiohttp pynput qrcode

# Jalankan server
python3 server.py
```

---

## 🔥 Buka Firewall (jika HP tidak bisa terhubung)

**Ubuntu/Debian:**
```bash
sudo ufw allow 8080/tcp
```

**Fedora/RHEL:**
```bash
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

---

## 📱 Cara Pakai di HP

1. Jalankan server di PC
2. Scan **QR Code** yang muncul di terminal, ATAU buka browser HP ketik:
   ```
   http://<IP-PC>:8080
   ```
3. Putar HP ke **Landscape** untuk pengalaman terbaik
4. Tekan **⛶ Fullscreen** untuk layar penuh

---

## ❓ Troubleshooting

| Masalah | Solusi |
|---|---|
| `Site can't be reached` | PC & HP harus di WiFi yang sama. Buka firewall (lihat di atas). |
| Keyboard tidak bereaksi di PC | Jalankan dari terminal di dalam sesi desktop GUI (bukan SSH) |
| `failed to acquire X connection` | Jalankan `export DISPLAY=:0` sebelum `python3 server.py` |
| Port 8080 sudah dipakai | Ganti port: `PORT=9090 python3 server.py` |
