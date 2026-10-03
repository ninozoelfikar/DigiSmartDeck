# 📐 System Architecture & Technical Specification / Arsitektur Sistem & Spesifikasi Teknis

*Read in: [Bahasa Indonesia](#-arsitektur-sistem-bahasa-indonesia) | [English](#-system-architecture-english)*

---

## 🇮🇩 Arsitektur Sistem (Bahasa Indonesia)

Dokumen ini menjelaskan desain arsitektur internal, alur data, protokol komunikasi, subsistem pemulihan jaringan, state machine tombol modifier, dan spesifikasi teknis dari **DigiSmartDeck**.

### 1. Diagram Alur Arsitektur

```mermaid
flowchart TD
    subgraph MobileDevice["📱 Perangkat Mobile (Android App / Browser HP / PWA)"]
        UI["Virtual PC Keyboard, Laptop Trackpad & Settings Studio UI"]
        TouchLogic["Touch, Multi-Touch & Trackpad Gesture Engine"]
        ModState["Client Persistent Modifier State Machine\n(Lock / 1-Shot / Hold)"]
        AudioHaptic["Web Audio API & Vibration Engine"]
        NetWatchdog["Self-Healing Network Subsystem\n(5.5s Watchdog, Backoff, Subnet Scanner)"]
        PWA["Service Worker & Offline Cache (PWA)"]
        
        subgraph NativeAndroid["🤖 Android Native App (DigiSmartDeck.apk)"]
            Immersive["True Immersive Sticky Fullscreen\n(Zero Chrome Popup / Toast)"]
            Bridge["DigiAndroidBridge (JS Interface)"]
            BtHid["Bluetooth HID Hardware Emulation\n(Keyboard + Mouse Composite HID)"]
            Immersive --> Bridge
            Bridge --> BtHid
        end
        
        WSClient["WebSocket Client (ws://<PC_IP>:8080/ws)"]
        
        UI --> TouchLogic
        TouchLogic --> ModState
        TouchLogic --> AudioHaptic
        ModState --> WSClient
        TouchLogic --> WSClient
        NetWatchdog <--> WSClient
        TouchLogic -.->|Direct Native Input| Bridge
    end

    subgraph DirectBtLink["📡 Direct Bluetooth Wireless Link (Zero Server Software)"]
        BtHid <-->|Standard Bluetooth HID Profile (L2CAP)| TargetPC["💻 Target PC / Mac / Smart TV / Tablet"]
    end

    subgraph LocalNetwork["📶 Jaringan Wi-Fi Lokal / mDNS"]
        WSClient <-->|WebSocket: ws://<PC_IP>:8080/ws| WSServer
        NetWatchdog -.->|Parallel Subnet HTTP Probes :8080/api/version| WSServer
        mDNS["mDNS Hostname: http://Jarvis.local:8080"] -.-> WSClient
    end

    subgraph HostPC["💻 Host PC (Linux / Windows / macOS)"]
        PreFlight["System Pre-Flight Checker\n(system_checker.py: Port, uinput, Firewall)"]
        WSServer["HTTP & WebSocket Server (aiohttp)"]
        Arbitrator["Anti-Collision Controller Arbitrator\n(Single Active Controller / Standby Queue / Takeover)"]
        IPEngine["Smart Network Detector (psutil / socket)"]
        ServerActiveKeys["Server Active Keys State Machine\n(global ACTIVE_KEYS tracker)"]
        KeyTranslator["Keycode & OS Profile Translator\n(Windows / macOS / Ubuntu)"]
        MouseHandler["Mouse, Kinetic Scroll & Button Handler"]
        
        subgraph DualInputController["Dual Input Controller Pipeline"]
            UinputDriver["Linux Kernel uinput Hardware Driver\n(Login Screen, Lock Screen, Sudo Root)"]
            PynputFallback["pynput Input Controller\n(X11, Wayland, Win32, Cocoa)"]
        end
        
        OSInput["OS Input Pipeline (Kernel Virtual HID / Desktop Environment)"]

        PreFlight --> WSServer
        IPEngine --> WSServer
        WSServer --> Arbitrator
        Arbitrator -->|Active Controller Only| ServerActiveKeys
        Arbitrator -.->|Standby Mode: Inputs Dropped| Arbitrator
        ServerActiveKeys --> KeyTranslator
        KeyTranslator -->|Linux Kernel Direct| UinputDriver --> OSInput
        KeyTranslator -->|Fallback Driver| PynputFallback --> OSInput
        Arbitrator -->|Active Controller Only| MouseHandler
        MouseHandler --> PynputFallback --> OSInput
    end
```

### 2. Alur Kerja Komunikasi & Subsistem

1. **Inisialisasi Server & Deteksi Jaringan Cerdas:**
   - Server menjalankan `server.py` berbasis asynchronous event loop `aiohttp`.
   - Modul `get_local_ip_addresses()` secara otomatis memindai seluruh antarmuka jaringan fisik (Wi-Fi/LAN `192.168.x.x` atau `10.x.x.x`) menggunakan `psutil` dan memfilter antarmuka virtual/VPN (Cloudflare WARP, Docker, virbr, Tailscale).
   - Menghasilkan QR Code ASCII di terminal, mencetak URL HTTP lokal, serta mendukung resolusi mDNS lokal (`http://Jarvis.local:8080`).

2. **Koneksi Klien & Dukungan PWA Layar Penuh:**
   - Browser mobile memuat antarmuka web responsif dari route `/` (`index.html`).
   - Tersedia Web App Manifest (`manifest.json`), Service Worker (`sw.js`), dan ikon HD multi-resolusi yang memungkinkan instalasi *Add to Home Screen* (PWA) untuk pengalaman native layar penuh murni tanpa bilah URL browser dan tanpa peringatan popup Chrome saat tombol fullscreen ditekan.
   - Klien membuka koneksi WebSocket persisten dua arah ke `/ws` dengan pemantau ping/pong real-time (latensi 1–5 ms).

3. **Persistent Modifier Lock & State Machine Tombol (Paritas Keyboard Fisik):**
   - Mengetik kombinasi shortcut PC di layar sentuh memerlukan penanganan modifier yang fleksibel dan andal. DigiSmartDeck menerapkan state machine tombol aktif dua arah (Client & Server):
     - **Mode 🔒 Lock (Default):** Mengetuk `Shift`, `Ctrl`, `Alt`, atau `Win`/`Cmd` akan mengunci tombol tersebut secara terus-menerus di OS hingga pengguna mengetuknya kembali untuk melepaskan. Ini memberikan paritas 1:1 dengan keyboard fisik PC: pengguna dapat melakukan seleksi teks multi-baris (`Shift + ⬇️ + ⬇️`), navigasi tab aplikasi berturut-turut (`Alt + Tab + Tab`), dan pengetikan huruf kapital berkelanjutan tanpa modifier lepas otomatis.
     - **Mode ⚡ 1-Shot:** Mengetuk modifier mengunci status untuk tepat 1 karakter berikutnya, lalu otomatis melepas modifier setelah tombol ditekan.
     - **Mode 🖐️ Hold:** Modifier hanya aktif selama jari pengguna menyentuh layar, dan otomatis lepas saat jari diangkat.
   - **Server-Side Active Keys State Machine:** Modul `server.py` memelihara set global `ACTIVE_KEYS`. Saat perintah `simulate_tap` atau `keypress` diproses, server memeriksa `ACTIVE_KEYS` sehingga modifier yang sedang ditahan tidak dilepas secara prematur sebelum perintah `keyup` eksplisit diterima.

4. **Subsistem Pemulihan Mandiri Koneksi Wi-Fi (Self-Healing Network Recovery):**
   - **Watchdog Deteksi Socket Zombie:** Sistem heartbeat ping/pong dengan timer watchdog 5.5 detik. Jika router Wi-Fi me-reboot atau sinyal terputus tanpa sinyal TCP FIN/RST, klien mendeteksi putusnya koneksi dan menghancurkan socket zombie seketika.
   - **Reconnection Loop Cerdas:** Mencoba menyambung kembali secara otomatis dengan *exponential backoff* dan *random jitter* untuk mencegah badai koneksi.
   - **Event Listeners Layar & Jaringan:** Mendengarkan event `online`, `offline`, dan `visibilitychange` (seketika mencoba rekoneksi saat layar ponsel dinyalakan kembali dari saku atau sleep).
   - **Pemindai Subnet Paralel (Dynamic Subnet Scanner):** Jika router Wi-Fi me-reboot dan DHCP memberikan alamat IP baru kepada PC (misal dari `192.168.8.103` menjadi `192.168.8.100`), klien otomatis meluncurkan pemindai subnet paralel (batch 24 IP) pada port 8080 untuk memeriksa endpoint `/api/version`, mendeteksi IP baru PC, dan menawarkan rekoneksi 1-tap instan tanpa perlu scan QR ulang.
   - **mDNS Fallback:** Menyediakan resolusi nama domain lokal permanen (`http://Jarvis.local:8080`).

5. **Dual Input Controller Pipeline (Linux uinput & pynput Fallback):**
   - **Linux Kernel Virtual Hardware Driver (`uinput`):** Saat berjalan di Linux dengan izin akses `/dev/uinput` (dikonfigurasi via `setup-uinput.sh`), DigiSmartDeck mendaftarkan perangkat virtual keyboard pada level kernel Linux. Ini memungkinkan input keyboard berfungsi penuh pada Layar Login Display Manager (GDM/SDDM/LightDM), Lock Screen, terminal, dan prompt kata sandi root (`sudo`).
   - **Pynput Controller Fallback:** Jika `uinput` tidak tersedia atau saat berjalan di sistem operasi Windows dan macOS, DigiSmartDeck secara otomatis beralih ke controller `pynput` pada level *user space*.

6. **Penanganan Multi-Touch & Gesture Trackpad Laptop:**
   - Komponen sentuh diatur dengan `touch-action: none` dan `preventDefault()` menyeluruh untuk mengeliminasi zoom ganda, scroll bawaan browser, atau kemunculan keyboard virtual Android/iOS.
   - **Trackpad Gestures:**
     - 1 Jari: Menggerakkan kursor mouse PC secara kinetik (dibatasi throttling ~120fps demi responsivitas maksimal).
     - 1-Finger Tap: Mengirim klik kiri instan (`mouseclick: left`).
     - 2-Finger Tap: Mengirim klik kanan instan (`mouseclick: right`).
     - 2-Finger Vertical Swipe: Mengirim perintah scroll mousewheel PC secara kinetik (`mousescroll`).
     - Dedicated Buttons: Tombol fisik virtual klik kiri & kanan laptop deck dengan status visual `.active` dan dukungan aksi *drag-and-drop*.
     - **Sakelar On/Off Trackpad:** Opsi penonaktifan dek trackpad secara penuh dari menu Pengaturan, toolbar atas, dan tombol palm rest.

7. **Engine Umpan Balik Taktil (Haptic & Web Audio API):**
   - **Haptic:** Panggilan `navigator.vibrate` untuk motor getar ponsel cerdas (preset: Lembut 15ms, Normal 30ms, Kuat 50ms).
   - **Mechanical Click Synthesizer:** Dua osilator Web Audio API (`triangle` 1500Hz→350Hz untuk kejernihan speaker kecil HP + `sine` 300Hz→90Hz untuk resonansi akustik keyboard mekanik).
   - **Audio Context Unlocker:** Memastikan `audioCtx` langsung aktif (*resumed*) pada sentuhan layar pertama pengguna, melewati limitasi autoplay browser mobile.
   - **Pengontrol Volume Granular:** Pengaturan volume suara klik (10% s/d 100%) dan tombol uji suara di modal Pengaturan.


8. **Anti-Collision Single Active Controller Arbitration (Manajemen Anti-Tabrakan Multi-User):**
   - **Masalah:** Jika beberapa perangkat (HP anak, tablet, laptop lain) membuka URL DigiSmartDeck yang sama secara bersamaan, input keyboard dan kursor mouse akan saling tumpang tindih (*interleaved keystrokes* dan jitter mouse acak).
   - **Solusi Arbitrase Server-Side:**
     - `ACTIVE_CONTROLLER_WS` dan `ACTIVE_CONTROLLER_INFO`: Server menetapkan koneksi pertama yang terhubung sebagai **Pengendali Aktif** (`🟢 👑 Pengendali Aktif`).
     - **Mode Siaga Otomatis (Standby Mode):** Klien berikutnya yang terhubung secara otomatis ditempatkan dalam status `standby` (`🟡 ⚡ Siaga (Ambil Alih)`). Seluruh payload pengetikan dan pergerakan mouse dari klien standby diabaikan (*dropped/suppressed*) oleh server demi melindungi integritas sesi.
     - **Manual Takeover:** Pengguna di mode siaga dapat mengetuk badge siaga untuk mengirimkan event `{ "type": "takeover" }`. Server akan langsung memindahkan kendali aktif kepadanya dan mengabarkan status terbaru ke seluruh klien via broadcast WebSocket.
     - **Auto-Takeover Timeout (30 Detik):** Jika pengendali aktif tidak melakukan aktivitas (tidak ada input) selama 30 detik, klien lain yang mengirim input diizinkan mengambil alih kendali secara otomatis.
     - **Clean Modifier Release on Handoff/Disconnect:** Saat pengendali aktif terputus (*disconnect*) atau diambil alih, fungsi `release_all_client_keys()` otomatis melepas semua modifier OS yang tertahan (Shift, Ctrl, Alt, Win/Cmd) agar tombol fisik PC tidak "tersangkut" (*stuck keys*).

9. **Android Native Client & Bluetooth HID Hardware Emulation:**
   - **Android Native Wrapper (`DigiSmartDeck.apk`):**
     - Dibangun menggunakan Gradle 8.5 dan Android SDK 34 dengan arsitektur web-to-native terpadu (`WebView` + `DigiAndroidBridge`).
     - **True Immersive Sticky Fullscreen:** Menghilangkan batasan browser mobile Chrome seperti bilah navigasi OS, status bar, dan pop-up peringatan Chrome (*"Swipe down to exit fullscreen"*) yang kerap mengganggu.
     - Orientasi lanskap terkunci otomatis (*locked landscape*) dan layar dicegah mati (*Keep Screen Awake*).
     - Menekan pemunculan keyboard virtual bawaan ponsel (Gboard/Swiftkey) secara absolut.
   - **Bluetooth HID Composite Profile (`BluetoothHidHelper.java`):**
     - Menggunakan Android 9+ (API 28) `BluetoothHidDevice` untuk mendaftarkan ponsel sebagai perangkat keras **Bluetooth Human Interface Device (HID)** standar.
     - Menggunakan Report Descriptor USB HID komposit standar (Keyboard 8-byte report format + Mouse 4-byte report format).
     - **Zero Server Software Needed:** Ponsel dapat langsung di-pair via Bluetooth ke PC Windows, Mac, Linux, iPad, Android TV, atau Smart TV dan langsung berfungsi sebagai keyboard & mouse nirkabel tanpa perlu menginstall software apa pun di komputer target.

10. **System Pre-Flight Diagnostics Engine & Standalone Packaging:**
    - **Pemeriksa Pra-Jalan Interaktif (`system_checker.py`):**
      - Dirancang khusus agar ramah bagi pengguna awam (zero-panic, zero-traceback).
      - **Pendeteksi Tabrakan Port 8080:** Jika port 8080 telah digunakan, sistem memeriksa apakah proses tersebut adalah daemon DigiSmartDeck yang sudah aktif. Jika ya, program menampilkan pesan sukses dan IP tanpa error. Jika digunakan aplikasi lain, sistem memandu pengguna dengan instruksi ramah.
      - **Otomatisasi Izin Kernel Linux (`/dev/uinput`):** Memeriksa hak akses uinput dan menawarkan perbaikan instan via `setfacl` tanpa restart.
      - **Pemeriksaan Firewall:** Memverifikasi status UFW pada Linux.
    - **Executable Mandiri (Zero-Python Installation):**
      - Linux: `build-linux.sh` menghasilkan binary mandiri ELF 64-bit `dist/DigiSmartDeck` (39MB).
      - Windows: `build-exe.bat` menghasilkan `dist/DigiSmartDeck.exe` mandiri via PyInstaller.
      - macOS: `build-macos.sh` menghasilkan `dist/DigiSmartDeckApp.app`.

---

### 3. Spesifikasi Protokol WebSocket

Komunikasi antara browser mobile dan host PC menggunakan payload JSON ringkas berkecepatan tinggi:

#### Payload Client ke Server:

1. **Keyboard Events:**
```json
// Penekanan tombol normal (dengan auto-repeat):
{
  "type": "keypress",
  "key": "a" | "enter" | "backspace" | null,
  "char": "a" | "A" | null,
  "modifiers": { "ctrl": false, "alt": false, "shift": false, "cmd": false }
}

// Penekanan & pelepasan tombol modifier (Persistent Lock / Hold):
{ "type": "keydown", "key": "shift" }
{ "type": "keyup", "key": "shift" }

// Shortcut / kombinasi simultan (1-tap):
{ "type": "combo", "keys": ["ctrl", "c"] }
```

2. **Trackpad & Mouse Events:**
```json
// Gerakan kursor kinetik:
{ "type": "mousemove", "dx": 12.5, "dy": -4.2 }

// Klik tombol mouse:
{ "type": "mouseclick", "button": "left" | "right" }
{ "type": "mousedown", "button": "left" | "right" }
{ "type": "mouseup", "button": "left" | "right" }

// Menggulir (Scroll):
{ "type": "mousescroll", "dx": 0, "dy": -3 }
```

3. **Arbitrase Pengendali (Controller Arbitration & Takeover):**
```json
// Permintaan ambil alih kendali aktif dari klien standby:
{ "type": "takeover" }
```

4. **Keepalive (Ping / Pong Heartbeat):**
```json
// Client:
{ "type": "ping" }

// Server Response:
{ "type": "pong" }
```

#### Payload Server ke Client:

1. **Status Pengendali Aktif vs Standby:**
```json
// Dikirim saat koneksi awal dan setiap kali ada pergantian status pengendali:
{
  "type": "controller_status",
  "status": "active" | "standby",
  "active_ip": "192.168.8.100",
  "active_ua": "Mozilla/5.0 (Linux; Android 14)...",
  "message": "Anda adalah pengendali aktif" | "Perangkat lain sedang mengendalikan PC"
}
```

---

## 🇬🇧 System Architecture (English)

This document outlines the internal architectural design, data pipelines, communication protocols, network self-healing subsystems, modifier key state machines, and technical specifications of **DigiSmartDeck**.

### 1. High-Level Architecture Overview

The system consists of two decoupled components communicating over a local high-speed WebSocket channel:
- **Client (Frontend):** Zero-dependency single-page HTML5/CSS3/ES6 web application and Progressive Web App (PWA). It features raw multi-touch event processing, persistent modifier latching, synthesized Web Audio acoustics, device vibration haptics, and a self-healing network watchdog with subnet auto-discovery.
- **Server (Backend):** Asynchronous Python daemon powered by `aiohttp`. It dispatches WebSocket payloads, tracks active key state machines, resolves host interfaces, and injects native hardware keyboard/mouse events via Linux kernel `uinput` or `pynput` user-space controllers.

### 2. Dual Input Controller Pipeline
To guarantee seamless input injection across all display managers and security environments, DigiSmartDeck implements a layered dual controller strategy:
1. **Linux Kernel Virtual Hardware Driver (`uinput`):**
   - Configured via `setup-uinput.sh` and `/dev/uinput` udev rules.
   - Emulates an authentic USB HID input device at the kernel level.
   - Operates in privileged contexts where standard user-space hooks fail: **Display Manager Login Screens (GDM, SDDM, LightDM)**, screen locks, and `sudo` password authentication prompts.
2. **Pynput Controller Fallback:**
   - Serves as the primary driver on Windows and macOS systems, and automatic fallback on Linux desktop environments when `uinput` is not provisioned.

### 3. Persistent Modifier Lock & State Machine
Typing desktop keyboard shortcuts on mobile touchscreens requires flexible modifier behavior. DigiSmartDeck provides three distinct modifier modes:
- **🔒 Lock Mode (Default):** Modifier keys (`Shift`, `Ctrl`, `Alt`, `Win`/`Cmd`) remain actively held down on the host operating system until tapped again to release. This mirrors real physical PC keyboard behavior, unlocking seamless multi-line text selection (`Shift + ⬇️ + ⬇️`), serialized window switching (`Alt + Tab + Tab`), continuous uppercase/symbol entry, and multi-key developer shortcuts.
- **⚡ 1-Shot Mode:** Modifier locks for exactly one subsequent keystroke, auto-releasing immediately after.
- **🖐️ Hold Mode:** Modifier remains active strictly while the user's finger is physically contacting the keycap.
- **Server-Side Active Key Tracking:** The backend server (`server.py`) maintains an authoritative `ACTIVE_KEYS` set. When processing standard `keypress` and `simulate_tap` events, the server checks `ACTIVE_KEYS` to ensure held modifier keys are never prematurely released before an explicit `keyup` event is received.

### 4. Self-Healing Wi-Fi Subsystem & Dynamic IP Discovery
Mobile clients frequently experience connection loss when host Wi-Fi routers reboot or DHCP reassigns IP addresses. DigiSmartDeck employs a resilient recovery stack:
1. **5.5s Heartbeat Ping/Pong Watchdog:** Unconditionally terminates zombie TCP sockets when no `pong` packet is received within 5.5 seconds, even if the mobile OS socket stack receives no TCP FIN/RST packet.
2. **Jittered Exponential Backoff:** Automatically re-establishes connection without flooding the host network.
3. **Screen-Wake & Network State Listeners:** Immediately triggers reconnect probes on `visibilitychange` (when waking from sleep or phone unlock) and `online` events.
4. **Parallel Subnet IP Scanner:** If the PC's IP address changes due to router reboot (e.g. from `192.168.8.103` to `192.168.8.100`), the client launches a background parallel scanner (batch size of 24 IPs) against port 8080 targeting `/api/version`. Upon finding the host, it presents a 1-tap reconnection prompt.
5. **Zero-Config mDNS:** Supports permanent local hostname resolution via `http://Jarvis.local:8080`.

### 5. Anti-Collision Single Active Controller Arbitration
When multiple mobile devices or family members open the DigiSmartDeck URL concurrently, concurrent uncoordinated keystrokes and trackpad motions would result in garbled text and erratic cursor jumping. DigiSmartDeck solves this through a server-side state machine:
- **Authoritative Controller:** The first client WebSocket to connect is designated as the **Active Controller** (`🟢 👑 Active Controller`).
- **Standby Isolation Mode:** Subsequent connecting clients automatically enter **Standby Mode** (`🟡 ⚡ Standby (Takeover)`). All typing, hotkey combinations, and mouse payloads from standby clients are dropped server-side to guarantee input session integrity.
- **Manual Takeover:** A standby user can tap the badge to dispatch `{ "type": "takeover" }`. The server transfers active control instantly and broadcasts updated status to all clients.
- **Auto-Takeover Timeout:** If the active controller is inactive for 30 seconds, any input from a standby client automatically transfers control.
- **Clean Modifier Release on Handoff/Disconnect:** Whenever an active session disconnects or is transferred, `release_all_client_keys()` releases any stuck OS modifiers (`Shift`, `Ctrl`, `Alt`, `Win`/`Cmd`).

### 6. Android Native Client & Bluetooth HID Composite Profile
- **Android Native App (`DigiSmartDeck.apk`):**
  - Compiled using Android SDK 34 and Gradle 8.5 with an optimized WebView architecture and `DigiAndroidBridge` JavaScript interface.
  - **True Immersive Sticky Fullscreen:** Completely eliminates Chrome browser bars, Android system gesture navigation bars, and the disruptive Chrome fullscreen warning toast.
  - Locked landscape orientation and screen keep-awake flag (`FLAG_KEEP_SCREEN_ON`).
  - Total suppression of native soft keyboard (Gboard/Swiftkey) popups.
- **Bluetooth HID Hardware Emulation (`BluetoothHidHelper.java`):**
  - Utilizes Android 9+ (API 28) `BluetoothHidDevice` to register the phone as a native Bluetooth Human Interface Device.
  - Uses standard composite USB HID Report Descriptors (Keyboard + Mouse).
  - **Zero Server Software Required:** Direct hardware pairing to Windows, Mac, Linux, iPad, Android TV, or Smart TV.

### 7. System Pre-Flight Diagnostics Engine & Standalone Packaging
- **Interactive Pre-Flight Checker (`system_checker.py`):**
  - Designed for non-technical users with zero traceback panic.
  - Detects port 8080 conflicts intelligently: if the port is already used by an active DigiSmartDeck systemd daemon, it prints a clean success message and IP URLs without errors.
  - Automatically verifies and provisions Linux `/dev/uinput` permissions using `setfacl`.
  - Audits Linux UFW firewall status.
- **Standalone Binary Packaging:**
  - Linux standalone 64-bit ELF binary `dist/DigiSmartDeck` (39MB) via `build-linux.sh`.
  - Windows standalone `dist/DigiSmartDeck.exe` via `build-exe.bat`.
  - macOS standalone bundle `dist/DigiSmartDeckApp.app` via `build-macos.sh`.
