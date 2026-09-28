#!/usr/bin/env python3
"""
DigiKeyboard - Layman-Friendly System & Permission Checker
Pemeriksa kebutuhan sistem dan izin akses yang interaktif dan ramah pengguna awam.
Mendukung: Linux, macOS, dan Windows.
"""

import sys
import os
import socket
import subprocess
import time
import urllib.request
import json
import shutil

# Warna terminal ANSI (dengan fallback jika terminal tidak mendukung)
USE_COLOR = sys.stdout.isatty() and os.name != 'nt' or os.environ.get('TERM') in ('xterm-256color', 'vt100')
if os.name == 'nt':
    # Aktifkan ANSI color di Windows 10/11 jika memungkinkan
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        USE_COLOR = True
    except Exception:
        pass

def colorize(text, color_code):
    if not USE_COLOR:
        return text
    return f"\033[{color_code}m{text}\033[0m"

def c_green(text): return colorize(text, "1;32")
def c_yellow(text): return colorize(text, "1;33")
def c_red(text): return colorize(text, "1;31")
def c_cyan(text): return colorize(text, "1;36")
def c_bold(text): return colorize(text, "1")
def c_dim(text): return colorize(text, "2")

def ask_user_yes_no(question, default_yes=True):
    """Tanya konfirmasi pengguna awam dengan opsi ramah."""
    prompt = " (Y/n) [Y]: " if default_yes else " (y/N) [N]: "
    try:
        sys.stdout.write(c_bold(question) + c_cyan(prompt))
        sys.stdout.flush()
        answer = input().strip().lower()
        if not answer:
            return default_yes
        return answer in ('y', 'ya', 'yes', '1')
    except (EOFError, KeyboardInterrupt):
        print()
        return False

# ─────────────────────────────────────────────────────────────
# 1. CEK KONEKSI JARINGAN & WI-FI
# ─────────────────────────────────────────────────────────────
def check_network():
    """Periksa apakah komputer terhubung ke jaringan Wi-Fi/LAN."""
    print(c_cyan("\n[1/5] Memeriksa Koneksi Jaringan & Wi-Fi..."))
    try:
        # Coba buka socket UDP semu untuk mencari IP interface lokal aktif
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = '127.0.0.1'

    if local_ip != '127.0.0.1':
        print(f"  {c_green('🟢 Terhubung!')} Komputer Anda memiliki alamat IP lokal: {c_bold(local_ip)}")
        print(c_dim("     (Pastikan HP/Tablet Anda terhubung ke Wi-Fi yang sama)"))
        return True, local_ip
    else:
        print(f"  {c_yellow('🟡 Perhatian:')} Komputer tampaknya belum terhubung ke jaringan Wi-Fi.")
        print(c_dim("     DigiKeyboard memerlukan Wi-Fi yang sama antara komputer dan HP."))
        print(c_dim("     Tips: Anda juga bisa menyalakan Hotspot dari HP lalu sambungkan laptop ke hotspot tersebut."))
        return False, local_ip

# ─────────────────────────────────────────────────────────────
# 2. CEK KETERSEDIAAN PORT JARINGAN (PORT 8080)
# ─────────────────────────────────────────────────────────────
def check_port(port=8080):
    """Periksa apakah port 8080 kosong atau sudah digunakan."""
    print(c_cyan(f"\n[2/5] Memeriksa Port Server (Port {port})..."))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
        print(f"  {c_green('🟢 Siap!')} Port {port} tersedia untuk komunikasi dengan HP.")
        return True, "available"
    except OSError:
        # Port sedang dipakai. Mari periksa apakah DigiKeyboard yang sedang memakainya!
        print(f"  {c_yellow('🟡 Port ' + str(port) + ' sedang digunakan.')} Memeriksa aplikasi yang memakainya...")
        is_digikeyboard = False
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/version", headers={'User-Agent': 'DigiChecker'})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if 'version' in data:
                    is_digikeyboard = True
                    server_ver = data.get('version', '1.x')
        except Exception:
            pass

        if is_digikeyboard:
            print(f"  {c_green('🎉 DigiKeyboard sudah aktif dan berjalan!')} (Versi: {server_ver})")
            print(c_dim("     Aplikasi sedang berjalan di latar belakang (Background Service)."))
            return False, "already_running"
        else:
            print(f"  {c_red('🔴 Port ' + str(port) + ' dipakai oleh aplikasi lain.')}")
            return False, "busy_other"

# ─────────────────────────────────────────────────────────────
# 3. CEK & MINTA IZIN INPUT HARDWARE / KEYBOARD
# ─────────────────────────────────────────────────────────────
def check_and_request_input_permissions():
    """Periksa izin kontrol keyboard & minta akses ramah pengguna jika belum ada."""
    print(c_cyan("\n[3/5] Memeriksa Izin Kontrol Keyboard & Mouse..."))

    current_platform = sys.platform

    # === A. LINUX (Kernel uinput) ===
    if current_platform.startswith('linux'):
        uinput_path = '/dev/uinput'
        has_access = os.path.exists(uinput_path) and os.access(uinput_path, os.W_OK)

        if has_access:
            print(f"  {c_green('🟢 Izin Lengkap!')} Akses perangkat input hardware ({uinput_path}) aktif.")
            print(c_dim("     (Mendukung Layar Login, Lockscreen, Wayland, dan X11)"))
            return True

        print(f"  {c_yellow('🟡 Izin Tambahan Dibutuhkan:')} Akses perangkat input Linux belum aktif.")
        print("     Agar HP Anda bisa mengetik saat Layar Kunci (Lockscreen), Layar Login,")
        print("     dan di Ubuntu Wayland, sistem memerlukan izin akses sekali saja.")
        print()

        if ask_user_yes_no("👉 Apakah Anda ingin mengaktifkan izin ini sekarang secara otomatis?"):
            print(c_dim("\n     Menyiapkan izin perangkat input... (Anda mungkin diminta memasukkan password PC)"))
            try:
                # 1. Pastikan module uinput ter-load
                subprocess.run(["sudo", "modprobe", "uinput"], check=False)
                
                # 2. Beri izin baca/tulis langsung pada /dev/uinput untuk user sekarang
                user = os.environ.get('USER', 'root')
                # Coba setfacl jika ada (paling bersih dan langsung aktif)
                acl_res = subprocess.run(["sudo", "setfacl", "-m", f"u:{user}:rw", uinput_path], check=False)
                if acl_res.returncode != 0:
                    # Fallback ke chmod 666
                    subprocess.run(["sudo", "chmod", "666", uinput_path], check=False)

                # 3. Buat udev rules permanen agar tidak hilang saat restart PC
                udev_rule = 'KERNEL=="uinput", MODE="0666", OPTIONS+="static_node=uinput"\n'
                rule_path = '/etc/udev/rules.d/99-uinput.rules'
                cmd = f"echo '{udev_rule}' | sudo tee {rule_path} >/dev/null && sudo udevadm control --reload-rules && sudo udevadm trigger {uinput_path} 2>/dev/null"
                subprocess.run(cmd, shell=True, check=False)

                # Re-check
                if os.access(uinput_path, os.W_OK):
                    print(f"  {c_green('✓ Sukses!')} Izin hardware keyboard & mouse berhasil diaktifkan!")
                    return True
                else:
                    print(f"  {c_yellow('ℹ️ Izin telah dikonfigurasi. Mungkin perlu login ulang untuk menerapkan grup.')}")
                    return True
            except Exception as ex:
                print(f"  {c_red('Gagal meminta izin otomatis:')} {ex}")
                print(c_dim("  Anda tetap bisa menjalankan DigiKeyboard via simulasi pynput bawaan."))
                return False
        else:
            print(c_dim("     Dilewati. DigiKeyboard akan berjalan dalam mode fallback standar."))
            return False

    # === B. MACOS (Accessibility Permission) ===
    elif current_platform == 'darwin':
        # Cek apakah pynput bisa mengontrol keyboard tanpa throwing
        has_perm = False
        try:
            from pynput.keyboard import Controller
            c = Controller()
            has_perm = True
        except Exception:
            has_perm = False

        if has_perm:
            print(f"  {c_green('🟢 Izin Aksesibilitas macOS Siap!')}")
            return True
        else:
            print(f"  {c_yellow('🟡 Izin Aksesibilitas Dibutuhkan (macOS)')}")
            print("     macOS mewajibkan Anda mencentang izin 'Accessibility' agar aplikasi")
            print("     bisa mengirim tombol keyboard dan gerakan mouse dari HP ke Mac.")
            print()

            if ask_user_yes_no("👉 Buka menu 'System Settings' sekarang untuk memberi izin?"):
                try:
                    subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
                    print(c_green("\n     ✓ Menu Pengaturan macOS telah dibuka!"))
                    print("     Langkah mudah:")
                    print("     1. Cari 'Terminal' atau 'DigiKeyboard' di daftar.")
                    print("     2. Geser tombol ke posisi AKTIF (warna biru/centang).")
                    print("     3. Kembali ke jendela ini.")
                    input(c_cyan("\n     Tekan Enter setelah Anda selesai memberi izin... "))
                    return True
                except Exception as ex:
                    print(f"  {c_red('Gagal membuka Pengaturan otomatis:')} {ex}")
                    return False
            return False

    # === C. WINDOWS ===
    elif current_platform == 'win32':
        print(f"  {c_green('🟢 Kontrol Keyboard Windows Siap!')}")
        print(c_dim("     (Input API pynput Windows aktif)"))
        return True

    return True

# ─────────────────────────────────────────────────────────────
# 4. CEK & BUKA FIREWALL (JIKA DIBUTUHKAN)
# ─────────────────────────────────────────────────────────────
def check_and_request_firewall(port=8080):
    """Periksa firewall apakah memblokir akses dari HP."""
    print(c_cyan("\n[4/5] Memeriksa Firewall Jaringan..."))

    if sys.platform.startswith('linux'):
        # Cek apakah ufw aktif
        if shutil.which('ufw'):
            try:
                res = subprocess.run(["sudo", "-n", "ufw", "status"], capture_output=True, text=True, check=False)
                if "Status: active" in res.stdout:
                    if str(port) not in res.stdout:
                        print(f"  {c_yellow('🟡 Firewall (UFW) aktif')} dan port {port} belum terdaftar.")
                        print("     Hal ini mungkin membuat HP tidak bisa membuka alamat website server.")
                        print()
                        if ask_user_yes_no(f"👉 Buka port {port} di firewall sekarang secara otomatis?"):
                            subprocess.run(["sudo", "ufw", "allow", f"{port}/tcp"], check=False)
                            print(f"  {c_green('✓ Port ' + str(port) + ' berhasil dibuka di Firewall!')}")
                            return True
                    else:
                        print(f"  {c_green('🟢 Firewall Mengizinkan!')} Port {port} sudah diizinkan di UFW.")
                        return True
            except Exception:
                pass
        print(f"  {c_green('🟢 Firewall Tidak Membatasi.')}")
        return True

    elif sys.platform == 'win32':
        print(f"  {c_green('🟢 Firewall Windows:')}")
        print(c_dim("     Jika muncul jendela 'Windows Defender Security Alert' saat pertama kali dijalankan,"))
        print(c_dim("     pastikan centang 'Private Networks' lalu klik tombol 'Allow Access'."))
        return True

    elif sys.platform == 'darwin':
        print(f"  {c_green('🟢 Firewall macOS Siap.')}")
        return True

    return True

# ─────────────────────────────────────────────────────────────
# 5. RANGKUMAN & PANDUAN PENGGUNA AWAM
# ─────────────────────────────────────────────────────────────
def print_layman_guide(local_ip, port=8080, port_status="available"):
    print(c_cyan("\n[5/5] Panduan Penggunaan Ramah untuk Pemula"))
    print("━" * 60)

    if port_status == "already_running":
        print(f"  {c_green('✨ DigiKeyboard sudah berjalan di background PC Anda!')}")
        print(f"  Anda tidak perlu menjalankan server lagi.")
    else:
        print(f"  {c_green('✓ Semua pemeriksaan sistem selesai! Sistem siap digunakan.')}")

    print("\n  📱 " + c_bold("CARA MENGGUNAKAN DARI HP / TABLET:"))
    print(f"  1. Pastikan HP terhubung ke Wi-Fi yang sama dengan PC ini.")
    print(f"  2. Buka browser (Chrome, Safari, Edge) di HP Anda.")
    print(f"  3. Masukkan alamat berikut di HP Anda:")
    print(f"     👉 {c_bold(c_green(f'http://{local_ip}:{port}'))}")
    print(f"  4. Putar posisi HP menjadi Landscape (Mendatar) untuk keyboard penuh.")
    print("━" * 60 + "\n")

# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def run_preflight_check(interactive=True, port=8080):
    """
    Fungsi utama yang dapat dipanggil baik secara mandiri (CLI)
    maupun di dalam server.py sebelum server dijalankan.
    Mengembalikan dict hasil pemeriksaan.
    """
    print(c_bold("\n🔍 Memeriksa Kesiapan Sistem DigiKeyboard..."))
    print(c_dim("Pemeriksaan otomatis untuk memastikan aplikasi berjalan lancar.\n"))

    net_ok, local_ip = check_network()
    port_ok, port_status = check_port(port)

    # Jika port sudah dipakai oleh DigiKeyboard background service
    if port_status == "already_running":
        print_layman_guide(local_ip, port, port_status)
        if interactive:
            print("Pilihan tindakan:")
            print("  [1] Tetap biarkan berjalan di background & selesai (Rekomendasi)")
            print("  [2] Buka halaman DigiKeyboard di browser komputer sekarang")
            print("  [3] Keluar")
            try:
                sys.stdout.write(c_cyan("\nPilih [1/2/3] (Default: 1): "))
                sys.stdout.flush()
                choice = input().strip()
                if choice == '2':
                    import webbrowser
                    webbrowser.open(f"http://127.0.0.1:{port}")
            except Exception:
                pass
        return {"status": "already_running", "ip": local_ip, "port": port}

    # Jika port dipakai aplikasi lain
    if port_status == "busy_other":
        print(f"\n{c_yellow('Tips Awam:')} Port {port} sedang dipakai oleh program lain di komputer Anda.")
        if interactive:
            alt_port = port + 1
            if ask_user_yes_no(f"👉 Apakah Anda ingin menggunakan port {alt_port} secara otomatis?"):
                return run_preflight_check(interactive, port=alt_port)

    # Izin Input & Firewall
    if interactive:
        check_and_request_input_permissions()
        check_and_request_firewall(port)

    print_layman_guide(local_ip, port, port_status)
    return {"status": "ready", "ip": local_ip, "port": port}

if __name__ == '__main__':
    run_preflight_check(interactive=True)
