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
import time
from aiohttp import web

def load_version():
    v_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(v_file):
        try:
            with open(v_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception:
            pass
    return '1.4.1'

__version__ = load_version()

# ── Dual Input Controller Setup (uinput Kernel Driver & pynput Fallback) ──
KEYBOARD_AVAILABLE = False
keyboard_controller = None
Key = None

MOUSE_AVAILABLE = False
mouse_controller = None
MouseButton = None

UINPUT_AVAILABLE = False
uinput_device = None
KEY_NAME_TO_EVDEV = {}
CHAR_TO_EVDEV = {}

# 1. Coba inisialisasi Linux uinput (Kernel-Level Hardware Input)
# Ini memungkinkan pengetikan di Layar Login Ubuntu (GDM), Lock Screen, Wayland, dan X11
if sys.platform.startswith('linux'):
    try:
        import evdev
        from evdev import UInput, ecodes as e

        if os.path.exists('/dev/uinput') and os.access('/dev/uinput', os.W_OK):
            cap = {
                e.EV_KEY: [
                    # Special & Navigation
                    e.KEY_ESC, e.KEY_TAB, e.KEY_CAPSLOCK, e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT,
                    e.KEY_LEFTCTRL, e.KEY_RIGHTCTRL, e.KEY_LEFTALT, e.KEY_RIGHTALT,
                    e.KEY_LEFTMETA, e.KEY_RIGHTMETA, e.KEY_ENTER, e.KEY_BACKSPACE,
                    e.KEY_DELETE, e.KEY_SPACE, e.KEY_UP, e.KEY_DOWN, e.KEY_LEFT, e.KEY_RIGHT,
                    e.KEY_HOME, e.KEY_END, e.KEY_PAGEUP, e.KEY_PAGEDOWN, e.KEY_INSERT,
                    e.KEY_PRINT, e.KEY_SCROLLLOCK, e.KEY_PAUSE, e.KEY_NUMLOCK,
                    # Function Keys
                    e.KEY_F1, e.KEY_F2, e.KEY_F3, e.KEY_F4, e.KEY_F5, e.KEY_F6,
                    e.KEY_F7, e.KEY_F8, e.KEY_F9, e.KEY_F10, e.KEY_F11, e.KEY_F12,
                    # Number row
                    e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4, e.KEY_5,
                    e.KEY_6, e.KEY_7, e.KEY_8, e.KEY_9, e.KEY_0,
                    # Punctuation
                    e.KEY_MINUS, e.KEY_EQUAL, e.KEY_LEFTBRACE, e.KEY_RIGHTBRACE,
                    e.KEY_BACKSLASH, e.KEY_SEMICOLON, e.KEY_APOSTROPHE, e.KEY_GRAVE,
                    e.KEY_COMMA, e.KEY_DOT, e.KEY_SLASH,
                    # Letters A-Z
                    e.KEY_A, e.KEY_B, e.KEY_C, e.KEY_D, e.KEY_E, e.KEY_F, e.KEY_G,
                    e.KEY_H, e.KEY_I, e.KEY_J, e.KEY_K, e.KEY_L, e.KEY_M, e.KEY_N,
                    e.KEY_O, e.KEY_P, e.KEY_Q, e.KEY_R, e.KEY_S, e.KEY_T, e.KEY_U,
                    e.KEY_V, e.KEY_W, e.KEY_X, e.KEY_Y, e.KEY_Z,
                    # Numpad
                    e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4,
                    e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9,
                    e.KEY_KPENTER, e.KEY_KPPLUS, e.KEY_KPMINUS, e.KEY_KPASTERISK, e.KEY_KPSLASH, e.KEY_KPDOT,
                    # Mouse Buttons
                    e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE
                ],
                e.EV_REL: [
                    e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL
                ]
            }
            uinput_device = UInput(cap, name="DigiKeyboard Virtual USB Device", vendor=0x1234, product=0x5678)
            UINPUT_AVAILABLE = True
            KEYBOARD_AVAILABLE = True
            MOUSE_AVAILABLE = True
            print("[✓] Linux uinput Virtual Hardware Controller aktif.")
            print("    (Mendukung Layar Login Ubuntu GDM, Lock Screen, Wayland & X11)")

            KEY_NAME_TO_EVDEV = {
                'esc': e.KEY_ESC, 'tab': e.KEY_TAB, 'caps_lock': e.KEY_CAPSLOCK,
                'shift': e.KEY_LEFTSHIFT, 'ctrl': e.KEY_LEFTCTRL, 'alt': e.KEY_LEFTALT,
                'cmd': e.KEY_LEFTMETA, 'win': e.KEY_LEFTMETA, 'super': e.KEY_LEFTMETA, 'meta': e.KEY_LEFTMETA,
                'shift_l': e.KEY_LEFTSHIFT, 'shift_r': e.KEY_RIGHTSHIFT,
                'ctrl_l': e.KEY_LEFTCTRL, 'ctrl_r': e.KEY_RIGHTCTRL,
                'alt_l': e.KEY_LEFTALT, 'alt_r': e.KEY_RIGHTALT,
                'enter': e.KEY_ENTER, 'backspace': e.KEY_BACKSPACE,
                'delete': e.KEY_DELETE, 'space': e.KEY_SPACE, 'up': e.KEY_UP,
                'down': e.KEY_DOWN, 'left': e.KEY_LEFT, 'right': e.KEY_RIGHT,
                'home': e.KEY_HOME, 'end': e.KEY_END, 'page_up': e.KEY_PAGEUP,
                'page_down': e.KEY_PAGEDOWN, 'insert': e.KEY_INSERT,
                'print_screen': e.KEY_PRINT, 'scroll_lock': e.KEY_SCROLLLOCK,
                'pause': e.KEY_PAUSE, 'num_lock': e.KEY_NUMLOCK,
                'f1': e.KEY_F1, 'f2': e.KEY_F2, 'f3': e.KEY_F3, 'f4': e.KEY_F4,
                'f5': e.KEY_F5, 'f6': e.KEY_F6, 'f7': e.KEY_F7, 'f8': e.KEY_F8,
                'f9': e.KEY_F9, 'f10': e.KEY_F10, 'f11': e.KEY_F11, 'f12': e.KEY_F12,
            }

            CHAR_TO_EVDEV = {
                'a': (e.KEY_A, False), 'b': (e.KEY_B, False), 'c': (e.KEY_C, False), 'd': (e.KEY_D, False),
                'e': (e.KEY_E, False), 'f': (e.KEY_F, False), 'g': (e.KEY_G, False), 'h': (e.KEY_H, False),
                'i': (e.KEY_I, False), 'j': (e.KEY_J, False), 'k': (e.KEY_K, False), 'l': (e.KEY_L, False),
                'm': (e.KEY_M, False), 'n': (e.KEY_N, False), 'o': (e.KEY_O, False), 'p': (e.KEY_P, False),
                'q': (e.KEY_Q, False), 'r': (e.KEY_R, False), 's': (e.KEY_S, False), 't': (e.KEY_T, False),
                'u': (e.KEY_U, False), 'v': (e.KEY_V, False), 'w': (e.KEY_W, False), 'x': (e.KEY_X, False),
                'y': (e.KEY_Y, False), 'z': (e.KEY_Z, False),
                'A': (e.KEY_A, True),  'B': (e.KEY_B, True),  'C': (e.KEY_C, True),  'D': (e.KEY_D, True),
                'E': (e.KEY_E, True),  'F': (e.KEY_F, True),  'G': (e.KEY_G, True),  'H': (e.KEY_H, True),
                'I': (e.KEY_I, True),  'J': (e.KEY_J, True),  'K': (e.KEY_K, True),  'L': (e.KEY_L, True),
                'M': (e.KEY_M, True),  'N': (e.KEY_N, True),  'O': (e.KEY_O, True),  'P': (e.KEY_P, True),
                'Q': (e.KEY_Q, True),  'R': (e.KEY_R, True),  'S': (e.KEY_S, True),  'T': (e.KEY_T, True),
                'U': (e.KEY_U, True),  'V': (e.KEY_V, True),  'W': (e.KEY_W, True),  'X': (e.KEY_X, True),
                'Y': (e.KEY_Y, True),  'Z': (e.KEY_Z, True),
                '1': (e.KEY_1, False), '2': (e.KEY_2, False), '3': (e.KEY_3, False), '4': (e.KEY_4, False),
                '5': (e.KEY_5, False), '6': (e.KEY_6, False), '7': (e.KEY_7, False), '8': (e.KEY_8, False),
                '9': (e.KEY_9, False), '0': (e.KEY_0, False),
                '!': (e.KEY_1, True),  '@': (e.KEY_2, True),  '#': (e.KEY_3, True),  '$': (e.KEY_4, True),
                '%': (e.KEY_5, True),  '^': (e.KEY_6, True),  '&': (e.KEY_7, True),  '*': (e.KEY_8, True),
                '(': (e.KEY_9, True),  ')': (e.KEY_0, True),
                ' ': (e.KEY_SPACE, False),
                '\n': (e.KEY_ENTER, False), '\r': (e.KEY_ENTER, False),
                '\t': (e.KEY_TAB, False),
                '-': (e.KEY_MINUS, False),      '_': (e.KEY_MINUS, True),
                '=': (e.KEY_EQUAL, False),      '+': (e.KEY_EQUAL, True),
                '[': (e.KEY_LEFTBRACE, False),  '{': (e.KEY_LEFTBRACE, True),
                ']': (e.KEY_RIGHTBRACE, False), '}': (e.KEY_RIGHTBRACE, True),
                '\\': (e.KEY_BACKSLASH, False), '|': (e.KEY_BACKSLASH, True),
                ';': (e.KEY_SEMICOLON, False),  ':': (e.KEY_SEMICOLON, True),
                '\'': (e.KEY_APOSTROPHE, False), '"': (e.KEY_APOSTROPHE, True),
                '`': (e.KEY_GRAVE, False),      '~': (e.KEY_GRAVE, True),
                ',': (e.KEY_COMMA, False),      '<': (e.KEY_COMMA, True),
                '.': (e.KEY_DOT, False),        '>': (e.KEY_DOT, True),
                '/': (e.KEY_SLASH, False),      '?': (e.KEY_SLASH, True),
            }
        else:
            print("[i] Info: /dev/uinput belum memiliki izin tulis untuk user saat ini.")
            print("    Jalankan './setup-uinput.sh' untuk mengaktifkan dukungan Layar Login Ubuntu.")
    except Exception as e_init:
        print(f"[i] uinput detection skipped: {e_init}")

# 2. Inisialisasi pynput (sebagai controller utama di Windows/macOS atau fallback di Linux)
try:
    from pynput.keyboard import Controller, Key as PynputKey
    keyboard_controller = Controller()
    Key = PynputKey
    KEYBOARD_AVAILABLE = True
    print("[✓] pynput keyboard controller siap.")
except Exception as e:
    if not UINPUT_AVAILABLE:
        print(f"[!] Warning: pynput controller tidak dapat mengaitkan display saat ini: {e}")
        print("[i] Server tetap akan berjalan dalam mode simulasi / logging.")

try:
    from pynput.mouse import Controller as MouseController, Button as PynputMouseButton
    mouse_controller = MouseController()
    MouseButton = PynputMouseButton
    MOUSE_AVAILABLE = True
    print("[✓] pynput mouse/trackpad controller siap.")
except Exception as e:
    if not UINPUT_AVAILABLE:
        print(f"[!] Warning: pynput mouse controller gagal: {e}")

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


def get_evdev_code_for_key(k):
    """Mendapatkan evdev scancode dari key name atau pynput key"""
    if isinstance(k, int):
        return k
    if not k:
        return None
    s = str(k).lower()
    if s.startswith('key.'):
        s = s[4:]
    if s in KEY_NAME_TO_EVDEV:
        return KEY_NAME_TO_EVDEV[s]
    if hasattr(k, 'name') and k.name.lower() in KEY_NAME_TO_EVDEV:
        return KEY_NAME_TO_EVDEV[k.name.lower()]
    return None


def simulate_press(k):
    """Simulasi penekanan tombol (uinput driver level atau pynput fallback)"""
    if UINPUT_AVAILABLE and uinput_device and k is not None:
        try:
            import evdev.ecodes as e
            ev_code = get_evdev_code_for_key(k)
            if ev_code:
                uinput_device.write(e.EV_KEY, ev_code, 1)
                uinput_device.syn()
                return
            if isinstance(k, str) and len(k) == 1 and k in CHAR_TO_EVDEV:
                code, need_shift = CHAR_TO_EVDEV[k]
                if need_shift:
                    uinput_device.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    uinput_device.syn()
                uinput_device.write(e.EV_KEY, code, 1)
                uinput_device.syn()
                return
        except Exception as e_ui:
            print(f"[Error uinput press]: {e_ui}")

    if KEYBOARD_AVAILABLE and keyboard_controller and k is not None:
        try:
            pk = KEY_MAPPINGS.get(k.lower()) if (isinstance(k, str) and k.lower() in KEY_MAPPINGS) else k
            keyboard_controller.press(pk)
        except Exception as e:
            print(f"[Error] Press key {k}: {e}")
    else:
        print(f"[Simulasi Press] {k}")


def simulate_release(k):
    """Simulasi pelepasan tombol (uinput driver level atau pynput fallback)"""
    if UINPUT_AVAILABLE and uinput_device and k is not None:
        try:
            import evdev.ecodes as e
            ev_code = get_evdev_code_for_key(k)
            if ev_code:
                uinput_device.write(e.EV_KEY, ev_code, 0)
                uinput_device.syn()
                return
            if isinstance(k, str) and len(k) == 1 and k in CHAR_TO_EVDEV:
                code, need_shift = CHAR_TO_EVDEV[k]
                uinput_device.write(e.EV_KEY, code, 0)
                uinput_device.syn()
                if need_shift:
                    uinput_device.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    uinput_device.syn()
                return
        except Exception as e_ui:
            print(f"[Error uinput release]: {e_ui}")

    if KEYBOARD_AVAILABLE and keyboard_controller and k is not None:
        try:
            pk = KEY_MAPPINGS.get(k.lower()) if (isinstance(k, str) and k.lower() in KEY_MAPPINGS) else k
            keyboard_controller.release(pk)
        except Exception as e:
            print(f"[Error] Release key {k}: {e}")
    else:
        print(f"[Simulasi Release] {k}")


def simulate_tap(k):
    """Simulasi tap (tekan lalu lepas)"""
    if UINPUT_AVAILABLE and uinput_device and k is not None:
        try:
            import evdev.ecodes as e
            if isinstance(k, str) and len(k) == 1 and k in CHAR_TO_EVDEV:
                code, need_shift = CHAR_TO_EVDEV[k]
                if need_shift:
                    uinput_device.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    uinput_device.syn()
                uinput_device.write(e.EV_KEY, code, 1)
                uinput_device.syn()
                time.sleep(0.005)
                uinput_device.write(e.EV_KEY, code, 0)
                uinput_device.syn()
                if need_shift:
                    time.sleep(0.002)
                    uinput_device.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    uinput_device.syn()
                return

            ev_code = get_evdev_code_for_key(k)
            if ev_code:
                uinput_device.write(e.EV_KEY, ev_code, 1)
                uinput_device.syn()
                time.sleep(0.005)
                uinput_device.write(e.EV_KEY, ev_code, 0)
                uinput_device.syn()
                return
        except Exception as e_ui:
            print(f"[Error uinput tap]: {e_ui}")

    if KEYBOARD_AVAILABLE and keyboard_controller and k is not None:
        try:
            pk = KEY_MAPPINGS.get(k.lower()) if (isinstance(k, str) and k.lower() in KEY_MAPPINGS) else k
            keyboard_controller.tap(pk)
        except Exception as e:
            try:
                keyboard_controller.press(pk)
                keyboard_controller.release(pk)
            except Exception as e2:
                print(f"[Error] Tap key {k}: {e2}")
    else:
        print(f"[Simulasi Tap] {k}")


def simulate_mouse_move(dx, dy):
    """Simulasi pergerakan kursor mouse/trackpad"""
    if UINPUT_AVAILABLE and uinput_device:
        try:
            import evdev.ecodes as e
            uinput_device.write(e.EV_REL, e.REL_X, int(round(float(dx))))
            uinput_device.write(e.EV_REL, e.REL_Y, int(round(float(dy))))
            uinput_device.syn()
            return
        except Exception as e_ui:
            print(f"[Error uinput mouse move]: {e_ui}")

    if MOUSE_AVAILABLE and mouse_controller:
        try:
            mouse_controller.move(float(dx), float(dy))
        except Exception as e:
            print(f"[Error] Mouse move: {e}")


def simulate_mouse_click(button='left'):
    """Simulasi klik mouse (left / right / middle)"""
    if UINPUT_AVAILABLE and uinput_device:
        try:
            import evdev.ecodes as e
            btn = e.BTN_RIGHT if button == 'right' else (e.BTN_MIDDLE if button == 'middle' else e.BTN_LEFT)
            uinput_device.write(e.EV_KEY, btn, 1)
            uinput_device.syn()
            uinput_device.write(e.EV_KEY, btn, 0)
            uinput_device.syn()
            return
        except Exception as e_ui:
            print(f"[Error uinput mouse click]: {e_ui}")

    if MOUSE_AVAILABLE and mouse_controller and MouseButton:
        try:
            btn = MouseButton.right if button == 'right' else (MouseButton.middle if button == 'middle' else MouseButton.left)
            mouse_controller.click(btn)
        except Exception as e:
            print(f"[Error] Mouse click: {e}")


def simulate_mouse_down(button='left'):
    """Simulasi menahan tombol mouse (drag / select)"""
    if UINPUT_AVAILABLE and uinput_device:
        try:
            import evdev.ecodes as e
            btn = e.BTN_RIGHT if button == 'right' else (e.BTN_MIDDLE if button == 'middle' else e.BTN_LEFT)
            uinput_device.write(e.EV_KEY, btn, 1)
            uinput_device.syn()
            return
        except Exception as e_ui:
            print(f"[Error uinput mouse down]: {e_ui}")

    if MOUSE_AVAILABLE and mouse_controller and MouseButton:
        try:
            btn = MouseButton.right if button == 'right' else (MouseButton.middle if button == 'middle' else MouseButton.left)
            mouse_controller.press(btn)
        except Exception as e:
            print(f"[Error] Mouse down: {e}")


def simulate_mouse_up(button='left'):
    """Simulasi melepas tombol mouse"""
    if UINPUT_AVAILABLE and uinput_device:
        try:
            import evdev.ecodes as e
            btn = e.BTN_RIGHT if button == 'right' else (e.BTN_MIDDLE if button == 'middle' else e.BTN_LEFT)
            uinput_device.write(e.EV_KEY, btn, 0)
            uinput_device.syn()
            return
        except Exception as e_ui:
            print(f"[Error uinput mouse up]: {e_ui}")

    if MOUSE_AVAILABLE and mouse_controller and MouseButton:
        try:
            btn = MouseButton.right if button == 'right' else (MouseButton.middle if button == 'middle' else MouseButton.left)
            mouse_controller.release(btn)
        except Exception as e:
            print(f"[Error] Mouse up: {e}")


def simulate_mouse_scroll(dx, dy):
    """Simulasi scroll dua jari trackpad"""
    if UINPUT_AVAILABLE and uinput_device:
        try:
            import evdev.ecodes as e
            # Pada evdev, REL_WHEEL positif adalah scroll up, negatif scroll down
            uinput_device.write(e.EV_REL, e.REL_WHEEL, int(round(float(dy))))
            uinput_device.syn()
            return
        except Exception as e_ui:
            print(f"[Error uinput mouse scroll]: {e_ui}")

    if MOUSE_AVAILABLE and mouse_controller:
        try:
            mouse_controller.scroll(int(dx), int(dy))
        except Exception as e:
            print(f"[Error] Mouse scroll: {e}")


def get_local_ip_addresses():
    """Mengambil daftar IP lokal komputer di jaringan Wi-Fi/LAN"""
    ip_list = []
    try:
        import psutil
        lan_ips = []
        other_ips = []
        for iface, addrs in psutil.net_if_addrs().items():
            iface_lower = iface.lower()
            is_virtual = any(k in iface_lower for k in ['docker', 'br-', 'virbr', 'warp', 'tun', 'tap', 'veth'])
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    if not is_virtual and (addr.address.startswith('192.168.') or addr.address.startswith('10.')):
                        lan_ips.append(addr.address)
                    elif not is_virtual:
                        lan_ips.append(addr.address)
                    else:
                        other_ips.append(addr.address)
        for ip in lan_ips + other_ips:
            if ip not in ip_list:
                ip_list.append(ip)
    except Exception:
        pass

    try:
        # Hubungkan dummy socket untuk mengetahui IP rute utama
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(('8.8.8.8', 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip not in ip_list:
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
    ua = request.headers.get('User-Agent', 'Unknown')
    print(f"[+] Client terhubung dari: {client_ip} | UA: {ua}")

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
                    if mods.get('ctrl'):
                        simulate_press('ctrl')
                        applied_mods.append('ctrl')
                    if mods.get('alt'):
                        simulate_press('alt')
                        applied_mods.append('alt')
                    if mods.get('shift') and not char:
                        # Shift untuk special key
                        simulate_press('shift')
                        applied_mods.append('shift')
                    if mods.get('cmd'):
                        simulate_press('cmd')
                        applied_mods.append('cmd')

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

                elif msg_type == 'mousemove':
                    dx = data.get('dx', 0)
                    dy = data.get('dy', 0)
                    simulate_mouse_move(dx, dy)

                elif msg_type == 'mouseclick':
                    btn = data.get('button', 'left')
                    simulate_mouse_click(btn)

                elif msg_type == 'mousedown':
                    btn = data.get('button', 'left')
                    simulate_mouse_down(btn)

                elif msg_type == 'mouseup':
                    btn = data.get('button', 'left')
                    simulate_mouse_up(btn)

                elif msg_type == 'mousescroll':
                    dx = data.get('dx', 0)
                    dy = data.get('dy', 0)
                    simulate_mouse_scroll(dx, dy)

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[!] WS Error: {ws.exception()}")

    finally:
        # Lepaskan semua tombol yang masih tertahan jika koneksi terputus
        for k in active_keys:
            simulate_release(k)
        if MOUSE_AVAILABLE and mouse_controller and MouseButton:
            try:
                mouse_controller.release(MouseButton.left)
                mouse_controller.release(MouseButton.right)
            except Exception:
                pass
        print(f"[-] Client terputus: {client_ip}")

    return ws


# --- HTTP Index Handler ---
async def index_handler(request):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return web.FileResponse(os.path.join(static_dir, 'index.html'))


def print_banner(port, ips):
    primary_url = f"http://{ips[0]}:{port}"
    print("=" * 60)
    print(f"  ⌨️  REMOTE PC KEYBOARD SERVER v{__version__}  ⌨️")
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


async def api_version_handler(request):
    return web.json_response({'version': __version__, 'name': 'DigiKeyboard'})


def create_app():
    app = web.Application()
    static_dir = os.path.join(os.path.dirname(__file__), 'static')

    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_get('/api/version', api_version_handler)
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
