# 📱 Dokumen Spesifikasi Landing Page DigiSmartDeck (Berdasarkan MVP Nyata)
> **Khusus untuk Target Pengguna Non-Teknis & Siap Pakai di Google Stitch**
> *Status Aplikasi:* **MVP Siap Pakai (Versi 1.20)**
> *Platform Desain:* [Google Stitch](https://stitch.withgoogle.com)

---

## 1. Apa Saja yang BENAR-BENAR Sudah Bisa Dilakukan Aplikasi Ini Sekarang? (Kondisi Nyata MVP)

Berdasarkan kode program aplikasi saat ini, DigiSmartDeck memiliki **5 Mode Nyata** yang langsung aktif di layar HP Anda:

1. **Mode Keyboard Laptop Lengkap (Bukan Keyboard HP yang Bikin Pusing):**
   - Layar HP menampilkan bentuk tuts keyboard komputer sungguhan: lengkap dengan tombol `F1 s/d F12`, angka kalkulator (*Numpad*), tombol panah, `Ctrl`, `Alt`, `Enter`, dan `Backspace`.
   - Ada suara ketikan keyboard mekanik yang renyah dan getaran sentuh di jari (*Haptic*).
   - Layar tidak akan tertutup oleh keyboard bawaan HP (Gboard/Samsung Keyboard).

2. **Mode Trackpad / Mouse Sentuh Laptop:**
   - Layar HP jadi bidang sentuh mouse: geser 1 jari untuk gerakkan panah kursor, ketuk 1 jari untuk klik kiri, ketuk 2 jari untuk klik kanan, dan usap 2 jari untuk geser halaman web naik-turun.
   - Ada tombol fisik Klik Kiri dan Klik Kanan di bawahnya.

3. **Mode Dikte Suara & Tombol Bantuan Mengetik (AI Workstation):**
   - Bicara di mikrofon HP, suara Anda langsung berubah jadi tulisan di laptop secara otomatis tanpa henti (bebas dari batas 3 detik Google yang suka memotong kalimat).
   - Tombol sekali sentuh untuk perintah umum: *Copy, Paste, Enter besar, Lanjutkan*.

4. **Mode Remote Hiburan & Presentasi (Air Mouse):**
   - Kendalikan laptop dari kasur/sofa: atur volume speaker, jeda video YouTube/Netflix, ganti lagu Spotify.
   - Gerakkan kursor panah di layar laptop di udara hanya dengan memiringkan HP (seperti tongkat sihir / sensor giroskop).
   - Tombol ganti slide presentasi PowerPoint/Google Slides.

5. **Mode Stick Game (Gamepad Konsol):**
   - Tombol arah dan tombol `A-B-X-Y` di layar HP untuk main game santai atau emulator di PC tanpa perlu beli stik game mahal.

---

## 2. Pembedahan Masalah Nyata (Pain Points) Pengguna Awam

| Masalah yang Sering Bikin Kesal (Pain Point) | Solusi yang Nyata dari DigiSmartDeck MVP |
| :--- | :--- |
| **"Tombol keyboard laptop rusak/copot, servisnya mahal dan lama."** | Pakai HP sebagai keyboard darurat instan yang tombolnya lengkap sampai tombol F1-F12 dan angka. |
| **"Lagi rebahan di kasur/sofa nonton film di laptop, malas bangun cuma buat pause atau gedein suara."** | HP jadi remote jarak jauh: kecilkan volume, pause video, atau gerakkan mouse dari kasur. |
| **"Pegal ngetik tugas atau laporan panjang di laptop."** | Cukup bicara lewat mikrofon HP, kata-kata Anda langsung otomatis terketik di Microsoft Word atau chat laptop. |
| **"Mau presentasi tugas kuliah/kantor tapi gak punya alat remote pointer."** | Gerakkan HP di udara untuk geser slide presentasi dan arahkan panah di layar. |
| **"Punya HP Android lama nganggur di laci lemari."** | Pasang aplikasi ringan ini (~5.5 MB), HP lama Anda langsung bermanfaat jadi touchpad dan remote meja kerja. |
| **"Takut ribet setting-nya dan takut data ketikan/password diintip orang."** | Cukup scan barcode di layar laptop dan ketik 6 angka PIN. Bekerja 100% di jaringan rumah sendiri, tanpa internet luar, aman 100%. |

---

## 3. Paket Harga Resmi yang Ada di MVP

| Paket | Harga | Apa yang Didapat? |
| :--- | :---: | :--- |
| **Community Free** | **Rp 0 (Gratis)** | Keyboard PC lengkap, mouse touchpad, remote media hiburan, gamepad game, dan coba gratis fitur dikte suara selama 7 hari. |
| **Lifetime Pro** *(Paling Populer)* | **Rp 250.000** *(Sekali Bayar)* | Semua fitur di atas + Dikte suara tanpa batas seumur hidup + Semua tema warna tombol keren (OLED, Retro, Cyberpunk) tanpa langganan bulanan. |
| **Studio Team** | **Rp 750.000** | Untuk penggunaan multi-perangkat di kantor/studio dan bantuan instalasi prioritas. |

---

## 4. MASTER PROMPT GOOGLE STITCH (Khusus Audiens Awam & Sesuai Fitur Asli)

> **Cara Pakai:** Salin seluruh teks bahasa Inggris di bawah ini ke [stitch.withgoogle.com](https://stitch.withgoogle.com). Teks ini sudah dirancang khusus agar AI Google Stitch menggambar halaman dengan kata-kata manusiawi yang menyentuh masalah sehari-hari:

```text
Design a clean, friendly, and trustworthy landing page for "DigiSmartDeck" — a desktop utility app that turns your smartphone into a full wireless PC keyboard, laptop touchpad, and multimedia remote.

TARGET AUDIENCE:
Everyday computer users, students, work-from-home professionals, and movie watchers who are NOT technical. Speak directly to their daily struggles (broken laptop keyboards, movie night laziness from bed, typing fatigue, and expensive accessories).

DESIGN STYLE:
- Modern, clean Dark Mode (deep warm charcoal #090D13, bright friendly accents: soft cyan #58A6FF and emerald green #238636).
- Welcoming, intuitive layout similar to consumer apps like Apple, Notion, or Spotify.
- Zero confusing tech jargon. Use human, everyday language.

PAGE SECTIONS TO GENERATE:

1. TOP NAVBAR:
   - Logo: "DigiSmartDeck" with an icon of a laptop connecting to a phone.
   - Links: "What It Does", "Real Uses", "How It Connects", "Pricing", "FAQ".
   - Top Right Action: "Download Free App" (clean bright button) and "Get Pro (Rp 250k)".

2. HERO SECTION:
   - Badge: "💡 No Expensive Gadgets Needed • Use Any Phone or Tablet in Your Home".
   - Main Headline: "Your Phone is Now a Wireless Keyboard & Remote for Your Laptop".
   - Subheadline: "Watch movies from your bed, type with your voice when your hands are tired, or replace a broken laptop keyboard in 30 seconds. Works smoothly over your home Wi-Fi."
   - Dual Call-to-Action Buttons:
     * Primary: "Download Android App (5.5 MB - Free)"
     * Secondary: "Install on PC in 1 Click"
   - Trust Badges below buttons: "✓ 100% Private & Safe" • "✓ Works Offline" • "✓ 6-Digit PIN Secured".
   - Visual Showcase: An interactive 3D-angled illustration showing a cozy room desk: a laptop playing a video and a phone beside it showing large, clean touch buttons (Play/Pause, Volume Slider, Touchpad Area, Full PC Keys).

3. "EVERYDAY SITUATIONS WHERE IT SAVES YOUR DAY" (4 Relatable Cards):
   - Card 1: "Movie Night From Bed or Sofa" - Adjust volume, skip YouTube ads, and pause Netflix on your laptop without getting out of your warm blanket.
   - Card 2: "Voice Typing for Tired Fingers" - Speak into your phone microphone and watch your words appear instantly in your Word document or laptop chat.
   - Card 3: "Instant Replacement for Broken Keyboards" - Spilled water or broken keys on your laptop? Turn your phone into an emergency full keyboard with all F1-F12 keys and numpads.
   - Card 4: "Presentations Without a Laser Clicker" - Stand in front of your class or office meeting and wave your phone in the air to move PowerPoint slides and control the cursor.

4. "THE 5 SMART MODES IN YOUR POCKET" (Clean Tabs / Bento Cards):
   - Mode 1: "Full PC Keyboard" (Real computer keys with click sound, arrow keys, and calculator numpad without being covered by mobile Gboard).
   - Mode 2: "Smooth Laptop Touchpad" (Slide 1 finger for cursor, tap 2 fingers to right-click, 2 fingers to scroll web pages).
   - Mode 3: "Voice Dictation & Smart Actions" (Speak your thoughts without annoying 3-second cutoffs, plus big quick buttons for Copy, Paste, and Enter).
   - Mode 4: "Air Mouse & Media Controller" (Point and wave your phone like a magic wand to move the cursor on your laptop screen).
   - Mode 5: "Casual Gamepad" (Retro gaming controller with D-Pad and ABXY buttons for relaxing PC games).

5. "CONNECT IN 3 SUPER SIMPLE STEPS" (Illustrated Process):
   - Step 1: Open DigiSmartDeck on your computer.
   - Step 2: Open the app on your phone and type the 6-digit PIN shown on your computer screen.
   - Step 3: Done! Your phone is now your remote control. No complicated cables, no account registrations.

6. HONEST & TRANSPARENT PRICING (No Subscription Traps):
   - Tier 1: "Community Free" (Rp 0 / Forever) - Full PC keyboard, laptop touchpad, media controls, gamepad, and a 7-day free trial of unlimited voice typing.
   - Tier 2: "Lifetime Pro" (Rp 250.000 / One-Time Payment) [FEATURED] - Unlimited voice typing forever, all colorful themes (Cyber, Retro, OLED), lifetime updates. "Pay once, keep forever. No monthly bills."
   - Tier 3: "Studio / Office" (Rp 750.000) - For multi-device setups and priority support.

7. CLEAR FAQ FOR REGULAR USERS:
   - "Does it need internet?" -> No, it connects directly between your laptop and phone through your home Wi-Fi or USB cable.
   - "Will my typed passwords be saved?" -> Never. It has zero keystroke logging and works 100% on your own device.
   - "Is it difficult to set up?" -> Just scan a QR code and enter 6 numbers. Takes under 1 minute.

8. WARM CLOSING BANNER & FOOTER:
   - Headline: "Ready to make using your computer 10x more comfortable?"
   - Big Green Download Button: "Download Free Now"
   - Footnote: "Supports Windows, Mac, Linux laptops, and Android phones."
```
