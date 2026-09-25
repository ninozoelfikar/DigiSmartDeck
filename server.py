#!/usr/bin/env python3
"""
Remote PC Keyboard Server
Server Python multi-platform untuk menerima input keyboard dari HP/Tablet via browser.
"""

import sys
import os
import socket
import json
import asyncio
from aiohttp import web

# Keyboard Controller Setup
KEYBOARD_AVAILABLE = False
keyboard_controller = None
Key = None

try:
    from pynput.keyboard import Controller, Key as PynputKey
    keyboard_controller = Controller()
    Key = PynputKey
    KEYBOARD_AVAILABLE = True
    print("[✓] pynput keyboard controller berhasil diinisialisasi.")
except Exception as e:
    print(f"[!] Warning: pynput controller tidak dapat mengaitkan display saat ini: {e}")
    print("[i] Server tetap akan berjalan dalam mode simulasi / logging.")

# QR Code Support
HAS_QR = False
try:
    import qrcode
    HAS_QR = True
except ImportError:
    pass

# Key Mapping dictionary from client to pynput
KEY_MAPPINGS = {}
if Key is not None:
    KEY_MAPPINGS = {
        'esc': Key.esc,
        'tab': Key.tab,
        'caps_lock': Key.caps_lock,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'alt': Key.alt,
        'cmd': Key.cmd,
        'enter': Key.enter,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'space': Key.space,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right,
        'home': Key.home,
        'end': Key.end,
        'page_up': Key.page_up,
        'page_down': Key.page_down,
        'insert': Key.insert,
        'print_screen': Key.print_screen,
        'scroll_lock': Key.scroll_lock,
        'pause': Key.pause,
        'num_lock': Key.num_lock,
        'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
        'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
        'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
    }


def resolve_key(key_name):
    """Menerjemahkan nama key client string ke objek key pynput atau karakter"""
    if not key_name:
        return None
    key_name_lower = key_name.lower()
    if key_name_lower in KEY_MAPPINGS:
        return KEY_MAPPINGS[key_name_lower]
    return key_name


def simulate_press(k):
    """Simulasi penekanan tombol"""
    if KEYBOARD_AVAILABLE and keyboard_controller and k is not None:
        try:
            keyboard_controller.press(k)
        except Exception as e:
            print(f"[Error] Press key {k}: {e}")
    else:
        print(f"[Simulasi Press] {k}")


def simulate_release(k):
    """Simulasi pelepasan tombol"""
    if KEYBOARD_AVAILABLE and keyboard_controller and k is not None:
        try:
            keyboard_controller.release(k)
        except Exception as e:
            print(f"[Error] Release key {k}: {e}")
    else:
        print(f"[Simulasi Release] {k}")


def simulate_tap(k):
    """Simulasi tap (tekan lalu lepas)"""
    if KEYBOARD_AVAILABLE and keyboard_controller and k is not None:
        try:
            keyboard_controller.tap(k)
        except Exception as e:
            # Fallback jika karakter khusus tidak mendukung tap langsung
            try:
                keyboard_controller.press(k)
                keyboard_controller.release(k)
            except Exception as e2:
                print(f"[Error] Tap key {k}: {e2}")
    else:
        print(f"[Simulasi Tap] {k}")


def get_local_ip_addresses():
    """Mengambil daftar IP lokal komputer di jaringan Wi-Fi/LAN"""
    ip_list = []
    try:
        # Hubungkan dummy socket untuk mengetahui IP rute utama
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(('8.8.8.8', 80))
        primary_ip = s.getsockname()[0]
        s.close()
        ip_list.append(primary_ip)
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip not in ip_list and not ip.startswith('127.'):
                ip_list.append(ip)
    except Exception:
        pass

    if not ip_list:
        ip_list.append('127.0.0.1')
    return ip_list


# --- WebSocket Handler ---
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client_ip = request.remote
    print(f"[+] Client terhubung dari: {client_ip}")

    # Set tombol yang sedang ditekan untuk client ini
    active_keys = set()

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get('type')

                if msg_type == 'ping':
                    await ws.send_str(json.dumps({'type': 'pong'}))

                elif msg_type == 'keypress':
                    key_name = data.get('key')
                    char = data.get('char')
                    mods = data.get('modifiers', {})

                    target = resolve_key(key_name) if key_name else char

                    # Tekan modifier jika ada
                    applied_mods = []
                    if mods.get('ctrl') and Key:
                        simulate_press(Key.ctrl)
                        applied_mods.append(Key.ctrl)
                    if mods.get('alt') and Key:
                        simulate_press(Key.alt)
                        applied_mods.append(Key.alt)
                    if mods.get('shift') and Key and not char:
                        # Shift untuk special key
                        simulate_press(Key.shift)
                        applied_mods.append(Key.shift)
                    if mods.get('cmd') and Key:
                        simulate_press(Key.cmd)
                        applied_mods.append(Key.cmd)

                    # Kirim tombol utama
                    if target:
                        simulate_tap(target)

                    # Lepas modifier
                    for m in reversed(applied_mods):
                        simulate_release(m)

                elif msg_type == 'keydown':
                    key_name = data.get('key')
                    target = resolve_key(key_name)
                    if target:
                        simulate_press(target)
                        active_keys.add(target)

                elif msg_type == 'keyup':
                    key_name = data.get('key')
                    target = resolve_key(key_name)
                    if target:
                        simulate_release(target)
                        active_keys.discard(target)

                elif msg_type == 'combo':
                    # Eksekusi kombinasi tombol, contoh: ["ctrl", "c"]
                    combo_keys = data.get('keys', [])
                    resolved = [resolve_key(k) for k in combo_keys if resolve_key(k)]
                    # Tekan semua berurutan
                    for k in resolved:
                        simulate_press(k)
                    await asyncio.sleep(0.05)
                    # Lepas semua urutan terbalik
                    for k in reversed(resolved):
                        simulate_release(k)

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[!] WS Error: {ws.exception()}")

    finally:
        # Lepaskan semua tombol yang masih tertahan jika koneksi terputus
        for k in active_keys:
            simulate_release(k)
        print(f"[-] Client terputus: {client_ip}")

    return ws


# --- HTTP Index Handler ---
async def index_handler(request):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return web.FileResponse(os.path.join(static_dir, 'index.html'))


def print_banner(port, ips):
    primary_url = f"http://{ips[0]}:{port}"
    print("=" * 60)
    print("  ⌨️  REMOTE PC KEYBOARD SERVER  ⌨️")
    print("=" * 60)
    print("Aplikasi siap digunakan!")
    print("Buka browser di HP/Tablet Anda yang terhubung ke Wi-Fi yang sama:")
    for ip in ips:
        print(f"  👉 http://{ip}:{port}")
    print("-" * 60)

    if HAS_QR:
        print("Atau scan QR Code berikut dengan kamera HP Anda:")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=2,
        )
        qr.add_data(primary_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    print("Tekan Ctrl+C di terminal ini untuk mematikan server.")
    print("=" * 60)


def create_app():
    app = web.Application()
    static_dir = os.path.join(os.path.dirname(__file__), 'static')

    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/static/', path=static_dir, name='static')
    # Juga route langsung untuk style.css dan app.js jika diminta di root
    app.router.add_get('/style.css', lambda r: web.FileResponse(os.path.join(static_dir, 'style.css')))
    app.router.add_get('/app.js', lambda r: web.FileResponse(os.path.join(static_dir, 'app.js')))
    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    ips = get_local_ip_addresses()
    print_banner(port, ips)

    app = create_app()
    web.run_app(app, host='0.0.0.0', port=port, print=None)
