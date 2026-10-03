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
import glob
import shutil
import re
import subprocess
from aiohttp import web

from auth_manager import pairing_manager, license_manager

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

def load_version():
    v_file = os.path.join(BASE_DIR, 'VERSION')
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
ACTIVE_KEYS = set()

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
                    # Media & Playback Keys
                    e.KEY_PLAYPAUSE, e.KEY_NEXTSONG, e.KEY_PREVIOUSSONG,
                    e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_MUTE, e.KEY_STOPCD,
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
            print("[OK] Linux uinput Virtual Hardware Controller aktif.")
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
                'media_play_pause': e.KEY_PLAYPAUSE, 'play_pause': e.KEY_PLAYPAUSE,
                'media_next': e.KEY_NEXTSONG, 'next_track': e.KEY_NEXTSONG,
                'media_prev': e.KEY_PREVIOUSSONG, 'media_previous': e.KEY_PREVIOUSSONG, 'prev_track': e.KEY_PREVIOUSSONG,
                'volume_up': e.KEY_VOLUMEUP, 'media_volume_up': e.KEY_VOLUMEUP,
                'volume_down': e.KEY_VOLUMEDOWN, 'media_volume_down': e.KEY_VOLUMEDOWN,
                'volume_mute': e.KEY_MUTE, 'mute': e.KEY_MUTE, 'media_volume_mute': e.KEY_MUTE,
                'media_stop': e.KEY_STOPCD, 'stop': e.KEY_STOPCD,
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
    print("[OK] pynput keyboard controller siap.")
except Exception as e:
    if not UINPUT_AVAILABLE:
        print(f"[!] Warning: pynput controller tidak dapat mengaitkan display saat ini: {e}")
        print("[i] Server tetap akan berjalan dalam mode simulasi / logging.")

try:
    from pynput.mouse import Controller as MouseController, Button as PynputMouseButton
    mouse_controller = MouseController()
    MouseButton = PynputMouseButton
    MOUSE_AVAILABLE = True
    print("[OK] pynput mouse/trackpad controller siap.")
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
        'control': Key.ctrl,
        'alt': Key.alt,
        'option': Key.alt,
        'opt': Key.alt,
        'cmd': Key.cmd,
        'win': Key.cmd,
        'super': Key.cmd,
        'meta': Key.cmd,
        'windows': Key.cmd,
        'enter': Key.enter,
        'return': Key.enter,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'space': Key.space,
        ' ': Key.space,
        '\n': Key.enter,
        '\r': Key.enter,
        '\t': Key.tab,
        'shift_l': getattr(Key, 'shift_l', Key.shift),
        'shift_r': getattr(Key, 'shift_r', Key.shift),
        'ctrl_l': getattr(Key, 'ctrl_l', Key.ctrl),
        'ctrl_r': getattr(Key, 'ctrl_r', Key.ctrl),
        'alt_l': getattr(Key, 'alt_l', Key.alt),
        'alt_r': getattr(Key, 'alt_r', getattr(Key, 'alt_gr', Key.alt)),
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
        'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        'media_play_pause': getattr(Key, 'media_play_pause', None),
        'play_pause': getattr(Key, 'media_play_pause', None),
        'media_next': getattr(Key, 'media_next', None),
        'next_track': getattr(Key, 'media_next', None),
        'media_prev': getattr(Key, 'media_previous', None),
        'media_previous': getattr(Key, 'media_previous', None),
        'prev_track': getattr(Key, 'media_previous', None),
        'volume_up': getattr(Key, 'media_volume_up', None),
        'media_volume_up': getattr(Key, 'media_volume_up', None),
        'volume_down': getattr(Key, 'media_volume_down', None),
        'media_volume_down': getattr(Key, 'media_volume_down', None),
        'volume_mute': getattr(Key, 'media_volume_mute', None),
        'mute': getattr(Key, 'media_volume_mute', None),
        'media_volume_mute': getattr(Key, 'media_volume_mute', None),
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


def is_caps_lock_on():
    """Mendeteksi apakah Caps Lock pada sistem operasi host sedang aktif (ON)."""
    if sys.platform.startswith('linux'):
        # 1. Sysfs brightness (bekerja di Wayland, X11, GDM login screen, tty)
        for p in glob.glob('/sys/class/leds/*capslock*/brightness') + glob.glob('/sys/class/leds/*caps_lock*/brightness') + glob.glob('/sys/class/leds/*::capslock/brightness'):
            try:
                with open(p, 'r') as f:
                    val = f.read().strip()
                    if val.isdigit() and int(val) > 0:
                        return True
            except Exception:
                pass
        # 2. X11 via ctypes (fallback jika DISPLAY aktif)
        try:
            import ctypes
            x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
            display = x11.XOpenDisplay(None)
            if display:
                class XKeyboardState(ctypes.Structure):
                    _fields_ = [
                        ('k', ctypes.c_int), ('b', ctypes.c_int), ('p', ctypes.c_uint),
                        ('d', ctypes.c_uint), ('led_mask', ctypes.c_ulong),
                        ('g', ctypes.c_int), ('a', ctypes.c_char * 32)
                    ]
                kb = XKeyboardState()
                x11.XGetKeyboardControl(display, ctypes.byref(kb))
                x11.XCloseDisplay(display)
                return bool(kb.led_mask & 1)
        except Exception:
            pass
        return False
    elif sys.platform == 'win32':
        try:
            import ctypes
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        except Exception:
            return False
    elif sys.platform == 'darwin':
        try:
            import Quartz
            return bool(Quartz.CGEventSourceFlagsState(Quartz.kCGEventSourceStateCombinedSessionState) & Quartz.kCGEventFlagMaskAlphaShift)
        except Exception:
            return False
    return False


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
                code, base_need_shift = CHAR_TO_EVDEV[k]
                need_shift = base_need_shift
                if k.isalpha():
                    caps_on = is_caps_lock_on()
                    want_upper = k.isupper()
                    need_shift = (want_upper != caps_on)
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
            if isinstance(k, str) and len(k) == 1 and k.isalpha():
                caps_on = is_caps_lock_on()
                want_upper = k.isupper()
                target_k = (k.lower() if want_upper else k.upper()) if caps_on else k
                keyboard_controller.press(target_k)
            else:
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
                code, base_need_shift = CHAR_TO_EVDEV[k]
                need_shift = base_need_shift
                if k.isalpha():
                    caps_on = is_caps_lock_on()
                    want_upper = k.isupper()
                    need_shift = (want_upper != caps_on)
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
            if isinstance(k, str) and len(k) == 1 and k.isalpha():
                caps_on = is_caps_lock_on()
                want_upper = k.isupper()
                target_k = (k.lower() if want_upper else k.upper()) if caps_on else k
                keyboard_controller.release(target_k)
            else:
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
            shift_held = ('shift' in ACTIVE_KEYS or resolve_key('shift') in ACTIVE_KEYS)
            if isinstance(k, str) and len(k) == 1 and k in CHAR_TO_EVDEV:
                code, base_need_shift = CHAR_TO_EVDEV[k]
                need_shift = base_need_shift
                if k.isalpha():
                    caps_on = is_caps_lock_on()
                    want_upper = k.isupper()
                    need_shift = (want_upper != caps_on)

                if need_shift and not shift_held:
                    uinput_device.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    uinput_device.syn()
                uinput_device.write(e.EV_KEY, code, 1)
                uinput_device.syn()
                time.sleep(0.005)
                uinput_device.write(e.EV_KEY, code, 0)
                uinput_device.syn()
                if need_shift and not shift_held:
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
            if isinstance(k, str) and len(k) == 1 and k.isalpha():
                caps_on = is_caps_lock_on()
                want_upper = k.isupper()
                target_k = (k.lower() if want_upper else k.upper()) if caps_on else k
                keyboard_controller.tap(target_k)
            else:
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


SCREEN_SIZE_CACHE = None

def get_screen_size():
    """Mengambil resolusi layar host PC (lebar, tinggi)"""
    global SCREEN_SIZE_CACHE
    if SCREEN_SIZE_CACHE:
        return SCREEN_SIZE_CACHE
    if sys.platform.startswith('linux'):
        try:
            import subprocess
            out = subprocess.check_output(['xrandr'], timeout=1).decode('utf-8', errors='ignore')
            for line in out.splitlines():
                if '*' in line:
                    parts = line.split()
                    for p in parts:
                        if 'x' in p and p[0].isdigit():
                            w, h = p.split('+')[0].split('x')
                            SCREEN_SIZE_CACHE = (int(w), int(h))
                            return SCREEN_SIZE_CACHE
        except Exception:
            pass
    try:
        import tkinter
        root = tkinter.Tk()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        if w > 0 and h > 0:
            SCREEN_SIZE_CACHE = (w, h)
            return SCREEN_SIZE_CACHE
    except Exception:
        pass
    SCREEN_SIZE_CACHE = (1920, 1080)
    return SCREEN_SIZE_CACHE


def simulate_mouse_abs(rx, ry):
    """Simulasi posisi kursor absolut dari Mode Canvas (koordinat 0.0 - 1.0)"""
    sw, sh = get_screen_size()
    tx = int(round(float(rx) * sw))
    ty = int(round(float(ry) * sh))
    tx = max(0, min(sw - 1, tx))
    ty = max(0, min(sh - 1, ty))
    if MOUSE_AVAILABLE and mouse_controller:
        try:
            mouse_controller.position = (tx, ty)
        except Exception as e:
            print(f"[Error mouse abs]: {e}")


def set_system_volume(percent):
    """Menyetel volume master sistem (0 - 100%)"""
    try:
        val = max(0, min(100, int(percent)))
        if sys.platform.startswith('linux'):
            import subprocess
            try:
                subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f"{val}%"], timeout=1, check=False)
                return
            except Exception:
                pass
            try:
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f"{val}%"], timeout=1, check=False)
                return
            except Exception:
                pass
    except Exception as e:
        print(f"[Error set volume]: {e}")



def get_local_ip_addresses():
    """Mengambil daftar IP lokal komputer di jaringan Wi-Fi/LAN"""
    ip_list = []
    try:
        import psutil
        usb_ips = []
        lan_ips = []
        other_ips = []
        for iface, addrs in psutil.net_if_addrs().items():
            iface_lower = iface.lower()
            is_usb = any(k in iface_lower for k in ['usb', 'rndis'])
            is_virtual = not is_usb and any(k in iface_lower for k in [
                'docker', 'br-', 'virbr', 'warp', 'tun', 'tap', 'veth',
                'vethernet', 'hyper-v', 'vmware', 'virtualbox', 'wsl'
            ])
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    if is_usb:
                        usb_ips.append(addr.address)
                    elif not is_virtual and (addr.address.startswith('192.168.') or addr.address.startswith('10.')):
                        lan_ips.append(addr.address)
                    elif not is_virtual:
                        lan_ips.append(addr.address)
                    else:
                        other_ips.append(addr.address)
        for ip in usb_ips + lan_ips + other_ips:
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


def get_host_os():
    """Mendeteksi jenis sistem operasi komputer server"""
    if sys.platform.startswith('linux'):
        return 'ubuntu'
    elif sys.platform == 'darwin':
        return 'mac'
    return 'win'


# --- Smart App Context Tracking ---
CACHED_X11_ENV = None
CURRENT_APP_CONTEXT = {
    'app': 'Desktop',
    'title': '',
    'suggested_mode': 'standard',
    'class_name': '',
    'win_id': ''
}

def get_x11_env():
    global CACHED_X11_ENV
    if CACHED_X11_ENV is not None:
        return CACHED_X11_ENV

    env = dict(os.environ)
    if 'DISPLAY' not in env:
        try:
            for pid in os.listdir('/proc'):
                if not pid.isdigit():
                    continue
                try:
                    with open(f'/proc/{pid}/environ', 'rb') as f:
                        data = f.read()
                    if b'DISPLAY=' in data and b'XAUTHORITY=' in data:
                        parts = data.split(b'\x00')
                        d = dict(p.split(b'=', 1) for p in parts if b'=' in p)
                        env['DISPLAY'] = d.get(b'DISPLAY', b':1').decode('utf-8', 'ignore')
                        env['XAUTHORITY'] = d.get(b'XAUTHORITY', b'').decode('utf-8', 'ignore')
                        break
                except Exception:
                    continue
        except Exception:
            pass
    if 'DISPLAY' not in env:
        env['DISPLAY'] = ':1'
    if 'XAUTHORITY' not in env or not env['XAUTHORITY']:
        env['XAUTHORITY'] = '/run/user/1000/gdm/Xauthority'

    CACHED_X11_ENV = env
    return env

def classify_app_context(wm_classes, title):
    wm_str = ' '.join(wm_classes).lower()
    t_lower = title.lower()

    # 1. AI Workstation / Coding / Terminal
    ai_apps = [
        'code', 'vscode', 'cursor', 'windsurf', 'pycharm', 'intellij', 'sublime',
        'neovim', 'nvim', 'emacs', 'kate', 'gedit', 'atom',
        'gnome-terminal', 'terminal', 'alacritty', 'kitty', 'konsole', 'xterm',
        'wezterm', 'terminator', 'tilix', 'xfce4-terminal', 'lxterminal'
    ]
    if any(app in wm_str for app in ai_apps) or any(k in t_lower for k in ['chatgpt', 'claude.ai', 'deepseek', 'ollama']):
        if 'code' in wm_str or 'vscode' in wm_str:
            friendly = 'VS Code'
        elif 'cursor' in wm_str:
            friendly = 'Cursor'
        elif 'windsurf' in wm_str:
            friendly = 'Windsurf'
        elif 'pycharm' in wm_str:
            friendly = 'PyCharm'
        elif 'intellij' in wm_str:
            friendly = 'IntelliJ'
        elif 'terminal' in wm_str or 'alacritty' in wm_str or 'kitty' in wm_str or 'konsole' in wm_str:
            friendly = 'Terminal'
        elif wm_classes:
            friendly = wm_classes[-1].replace('-', ' ').title()
        else:
            friendly = 'AI Workstation'
        return 'ai', friendly

    # 2. Presentation
    present_apps = ['impress', 'powerpnt', 'powerpoint', 'keynote', 'wps', 'wpp', 'evince', 'okular', 'acroread', 'xreader', 'mupdf', 'atril', 'zathura']
    if any(app in wm_str for app in present_apps) or any(k in t_lower for k in ['slides.google.com', 'canva.com', 'pitch.com', 'presentation']):
        if 'impress' in wm_str:
            friendly = 'Impress Slides'
        elif 'evince' in wm_str or 'okular' in wm_str or 'pdf' in t_lower:
            friendly = 'Document Viewer'
        else:
            friendly = 'Presentation'
        return 'present', friendly

    # 3. Media
    media_apps = ['vlc', 'mpv', 'celluloid', 'totem', 'spotify', 'rhythmbox', 'clementine', 'audacious', 'kodi', 'plex']
    if any(app in wm_str for app in media_apps) or any(k in t_lower for k in ['youtube.com', 'netflix.com', 'spotify.com', 'twitch.tv']):
        if 'vlc' in wm_str:
            friendly = 'VLC Media Player'
        elif 'spotify' in wm_str:
            friendly = 'Spotify'
        elif 'mpv' in wm_str:
            friendly = 'MPV Player'
        elif 'youtube' in t_lower:
            friendly = 'YouTube'
        elif 'netflix' in t_lower:
            friendly = 'Netflix'
        else:
            friendly = 'Media Player'
        return 'media', friendly

    # 4. Gamepad / Emulators
    game_apps = ['steam', 'retroarch', 'pcsx2', 'dolphin-emu', 'dolphin', 'rpcs3', 'yuzu', 'ryujinx', 'lutris', 'heroic', 'wine', 'ppsspp', 'duckstation']
    if any(app in wm_str for app in game_apps):
        if 'steam' in wm_str:
            friendly = 'Steam'
        elif 'retroarch' in wm_str:
            friendly = 'RetroArch'
        else:
            friendly = 'Game / Emulator'
        return 'game', friendly

    # 5. Drawing / Graphics
    canvas_apps = ['gimp', 'krita', 'inkscape', 'blender', 'photoshop', 'illustrator', 'figma']
    if any(app in wm_str for app in canvas_apps):
        friendly = wm_classes[-1].capitalize() if wm_classes else 'Canvas'
        return 'canvas', friendly

    # 6. Standard / Browser / General
    if 'chrome' in wm_str:
        friendly = 'Google Chrome'
    elif 'firefox' in wm_str:
        friendly = 'Firefox'
    elif 'nautilus' in wm_str or 'files' in wm_str:
        friendly = 'File Manager'
    elif wm_classes:
        friendly = wm_classes[-1].replace('-', ' ').title()
    else:
        friendly = 'Desktop'

    return 'standard', friendly

def get_active_window_info():
    """Mendeteksi jendela aktif di PC host (Linux X11 dan fallback Windows)."""
    global CACHED_X11_ENV
    if sys.platform.startswith('linux'):
        try:
            env = get_x11_env()
            res = subprocess.run(
                ['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.6
            )
            if res.returncode != 0:
                CACHED_X11_ENV = None
                return None

            m = re.search(r'#\s*(0x[0-9a-fA-F]+)', res.stdout)
            if not m or m.group(1) == '0x0':
                return {
                    'app': 'Desktop',
                    'title': '',
                    'suggested_mode': 'standard',
                    'class_name': '',
                    'win_id': '0x0'
                }

            win_id = m.group(1)
            res_info = subprocess.run(
                ['xprop', '-id', win_id, 'WM_CLASS', '_NET_WM_NAME', 'WM_NAME'],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.6
            )
            if res_info.returncode != 0:
                return {
                    'app': 'Desktop',
                    'title': '',
                    'suggested_mode': 'standard',
                    'class_name': '',
                    'win_id': win_id
                }

            out = res_info.stdout
            wm_classes = re.findall(r'"([^"]*)"', out.split('WM_CLASS(STRING) =')[-1].split('\n')[0]) if 'WM_CLASS' in out else []
            title_match = re.search(r'(?:_NET_WM_NAME\(UTF8_STRING\) = "([^"]*)"|WM_NAME\(STRING\) = "([^"]*)")', out)
            title = ''
            if title_match:
                title = title_match.group(1) or title_match.group(2) or ''

            wm_str = ' '.join(wm_classes).lower()
            if 'digikeyboard_gui' in wm_str or ('digikeyboard' in wm_str and 'host' in wm_str) or 'host manager' in title.lower():
                return None

            suggested_mode, friendly_name = classify_app_context(wm_classes, title)
            return {
                'app': friendly_name,
                'title': title,
                'suggested_mode': suggested_mode,
                'class_name': wm_classes[0] if wm_classes else '',
                'win_id': win_id
            }
        except Exception:
            return None
    elif sys.platform == 'win32':
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return {'app': 'Desktop', 'title': '', 'suggested_mode': 'standard', 'class_name': '', 'win_id': '0'}
            title = win32gui.GetWindowText(hwnd) or ''
            class_name = win32gui.GetClassName(hwnd) or ''
            mode, friendly = classify_app_context([class_name], title)
            return {'app': friendly, 'title': title, 'suggested_mode': mode, 'class_name': class_name, 'win_id': str(hwnd)}
        except Exception:
            return None

    return None

def get_open_windows_list():
    """Mengambil daftar jendela aplikasi GUI yang terbuka di PC host."""
    global CACHED_X11_ENV, CURRENT_APP_CONTEXT
    windows = []
    current_active_id = CURRENT_APP_CONTEXT.get('win_id', '') if CURRENT_APP_CONTEXT else ''

    if sys.platform.startswith('linux'):
        try:
            env = get_x11_env()
            res = subprocess.run(
                ['wmctrl', '-l', '-x'],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.8
            )
            if res.returncode == 0:
                for line in res.stdout.strip().splitlines():
                    parts = re.split(r'\s+', line.strip(), maxsplit=4)
                    if len(parts) >= 5:
                        win_id, desktop_num, wm_class, client_machine, title = parts
                    elif len(parts) == 4:
                        win_id, desktop_num, wm_class, client_machine = parts
                        title = ''
                    else:
                        continue

                    try:
                        d_num = int(desktop_num)
                    except ValueError:
                        d_num = 0

                    wm_class_lower = wm_class.lower()
                    if d_num == -1:
                        if 'desktop' in wm_class_lower or 'gjs' in wm_class_lower or 'nautilus' in wm_class_lower:
                            continue

                    if not title or title.strip() == 'Desktop Icons':
                        continue

                    # Filter keluar aplikasi internal DigiKeyboard Host Manager / Installer sendiri
                    if 'digikeyboard_gui' in wm_class_lower or ('digikeyboard' in wm_class_lower and 'host' in wm_class_lower):
                        continue
                    if 'host manager' in title.lower() or title.strip() == 'DigiKeyboard Host':
                        continue

                    classes = [c for c in wm_class.split('.') if c]
                    suggested_mode, friendly_name = classify_app_context(classes, title)

                    is_active = False
                    if current_active_id:
                        try:
                            is_active = (int(win_id, 16) == int(current_active_id, 16))
                        except Exception:
                            is_active = (win_id.lower() == current_active_id.lower())

                    windows.append({
                        'win_id': win_id,
                        'app': friendly_name,
                        'title': title,
                        'suggested_mode': suggested_mode,
                        'class_name': wm_class,
                        'is_active': is_active
                    })
        except Exception:
            pass

    elif sys.platform == 'win32':
        try:
            import win32gui, win32process
            def enum_cb(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd) or ''
                    if title and title != 'Program Manager':
                        class_name = win32gui.GetClassName(hwnd) or ''
                        if 'digikeyboard' in class_name.lower() or 'host manager' in title.lower():
                            return
                        suggested_mode, friendly_name = classify_app_context([class_name], title)
                        is_active = (str(hwnd) == str(current_active_id))
                        extra.append({
                            'win_id': str(hwnd),
                            'app': friendly_name,
                            'title': title,
                            'suggested_mode': suggested_mode,
                            'class_name': class_name,
                            'is_active': is_active
                        })
            win32gui.EnumWindows(enum_cb, windows)
        except Exception:
            pass

    return windows


def activate_and_focus_window(win_id, maximize=True):
    """Mengangkat jendela PC ke depan dan memaksimalkan ukurannya."""
    global CACHED_X11_ENV
    if not win_id:
        return False
    if sys.platform.startswith('linux'):
        try:
            env = get_x11_env()
            # 1. Aktifkan dan angkat jendela ke depan (focus & raise)
            subprocess.run(
                ['wmctrl', '-i', '-a', win_id],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.8
            )
            # 2. Maksimalkan jendela jika diminta
            if maximize:
                subprocess.run(
                    ['wmctrl', '-i', '-r', win_id, '-b', 'add,maximized_vert,maximized_horz'],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=0.8
                )
            return True
        except Exception:
            return False
    elif sys.platform == 'win32':
        try:
            import win32gui, win32con
            hwnd = int(win_id)
            if win32gui.IsWindow(hwnd):
                if maximize:
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                else:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return True
        except Exception:
            return False
    return False

def minimize_window(win_id):
    """Meminimalkan (minimize) jendela PC host."""
    global CACHED_X11_ENV
    if not win_id:
        return False
    if sys.platform.startswith('linux'):
        try:
            env = get_x11_env()
            # Coba menggunakan ctypes libX11 XIconifyWindow (standar X11 asli)
            try:
                import ctypes
                x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
                x11.XOpenDisplay.restype = ctypes.c_void_p
                disp = x11.XOpenDisplay(env.get('DISPLAY', ':1').encode('utf-8'))
                if disp:
                    screen = x11.XDefaultScreen(ctypes.c_void_p(disp))
                    w_int = int(win_id, 16) if str(win_id).startswith('0x') else int(win_id)
                    x11.XIconifyWindow(ctypes.c_void_p(disp), ctypes.c_ulong(w_int), ctypes.c_int(screen))
                    x11.XFlush(ctypes.c_void_p(disp))
                    x11.XCloseDisplay(ctypes.c_void_p(disp))
                    return True
            except Exception:
                pass
            # Fallback ke wmctrl
            subprocess.run(
                ['wmctrl', '-i', '-r', win_id, '-b', 'add,hidden'],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.8
            )
            return True
        except Exception:
            return False
    elif sys.platform == 'win32':
        try:
            import win32gui, win32con
            hwnd = int(win_id)
            if win32gui.IsWindow(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return True
        except Exception:
            return False
    return False

def maximize_window(win_id):
    """Memaksimalkan (maximize) atau memulihkan (restore) ukuran jendela PC host."""
    global CACHED_X11_ENV
    if not win_id:
        return False
    if sys.platform.startswith('linux'):
        try:
            env = get_x11_env()
            subprocess.run(
                ['wmctrl', '-i', '-r', win_id, '-b', 'toggle,maximized_vert,maximized_horz'],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.8
            )
            return True
        except Exception:
            return False
    elif sys.platform == 'win32':
        try:
            import win32gui, win32con
            hwnd = int(win_id)
            if win32gui.IsWindow(hwnd):
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == win32con.SW_SHOWMAXIMIZED:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                else:
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                win32gui.SetForegroundWindow(hwnd)
                return True
        except Exception:
            return False
    return False

def close_window(win_id):
    """Menutup jendela PC host secara anggun (graceful close)."""
    global CACHED_X11_ENV
    if not win_id:
        return False
    if sys.platform.startswith('linux'):
        try:
            env = get_x11_env()
            subprocess.run(
                ['wmctrl', '-i', '-c', win_id],
                env=env,
                capture_output=True,
                text=True,
                timeout=0.8
            )
            return True
        except Exception:
            return False
    elif sys.platform == 'win32':
        try:
            import win32gui, win32con
            hwnd = int(win_id)
            if win32gui.IsWindow(hwnd):
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                return True
        except Exception:
            return False
    return False

async def smart_context_tracker_loop():
    """Background task memeriksa jendela aktif PC setiap 800ms dan memancarkan perubahan ke client."""
    global CURRENT_APP_CONTEXT
    while True:
        try:
            info = await asyncio.to_thread(get_active_window_info)
            if info:
                changed = (
                    info['suggested_mode'] != CURRENT_APP_CONTEXT['suggested_mode'] or
                    info['app'] != CURRENT_APP_CONTEXT['app'] or
                    info['win_id'] != CURRENT_APP_CONTEXT.get('win_id')
                )
                if changed:
                    CURRENT_APP_CONTEXT = info
                    payload = json.dumps({
                        'type': 'app_context',
                        'app': info['app'],
                        'title': info['title'],
                        'suggested_mode': info['suggested_mode'],
                        'class_name': info['class_name']
                    })
                    for client in list(CONNECTED_CLIENTS):
                        try:
                            await client.send_str(payload)
                        except Exception:
                            pass
        except asyncio.CancelledError:
            break
        except Exception:
            pass
        await asyncio.sleep(0.8)


# --- WebSocket Handler ---
CONNECTED_CLIENTS = set()

def get_device_label(request, data=None):
    if data and data.get('device_name'):
        return str(data.get('device_name'))
    ua = request.headers.get('User-Agent', '')
    ip = request.remote or '127.0.0.1'
    if 'Android' in ua:
        dev = 'Android'
    elif 'iPhone' in ua:
        dev = 'iPhone'
    elif 'iPad' in ua:
        dev = 'iPad'
    elif 'Macintosh' in ua:
        dev = 'Mac'
    elif 'Windows' in ua:
        dev = 'Windows'
    elif 'Linux' in ua:
        dev = 'Linux'
    else:
        dev = 'Perangkat'
    return f"{dev} ({ip})"

async def broadcast_controller_status():
    for client in list(CONNECTED_CLIENTS):
        try:
            await client.send_str(json.dumps({
                'type': 'controller_status',
                'role': 'active',
                'message': 'Perangkat terhubung sebagai Pengendali PC.'
            }))
        except Exception:
            pass

def release_all_client_keys(keys_set):
    for k in list(keys_set):
        simulate_release(k)
        ACTIVE_KEYS.discard(k)
    keys_set.clear()

async def websocket_handler(request):
    ws = web.WebSocketResponse(heartbeat=10.0, receive_timeout=25.0)
    await ws.prepare(request)
    CONNECTED_CLIENTS.add(ws)
    client_ip = request.remote
    ua = request.headers.get('User-Agent', 'Unknown')
    device_label = get_device_label(request)
    print(f"[+] Client terhubung: {client_ip} | {device_label} (Total terhubung: {len(CONNECTED_CLIENTS)})")

    # Inisialisasi status otentikasi client (localhost diizinkan cepat jika dev/usb)
    is_client_authorized = pairing_manager.is_authorized("", client_ip)
    client_token = None

    # Kirim handshake inisialisasi ke client
    try:
        await ws.send_str(json.dumps({
            'type': 'init',
            'version': __version__,
            'host_os': get_host_os(),
            'platform': sys.platform,
            'uinput_active': UINPUT_AVAILABLE,
            'caps_lock': is_caps_lock_on(),
            'pairing_required': not is_client_authorized,
            'host_name': socket.gethostname(),
            'license': license_manager.get_info()
        }))
        if is_client_authorized:
            await ws.send_str(json.dumps({
                'type': 'controller_status',
                'role': 'active',
                'message': 'Perangkat terhubung sebagai Pengendali PC.'
            }))
        else:
            await ws.send_str(json.dumps({
                'type': 'controller_status',
                'role': 'pairing_required',
                'message': 'Perangkat membutuhkan pairing dengan PIN PC.'
            }))
        await ws.send_str(json.dumps({
            'type': 'app_context',
            'app': CURRENT_APP_CONTEXT['app'],
            'title': CURRENT_APP_CONTEXT['title'],
            'suggested_mode': CURRENT_APP_CONTEXT['suggested_mode'],
            'class_name': CURRENT_APP_CONTEXT['class_name']
        }))
    except Exception:
        pass

    # Set tombol yang sedang ditekan untuk client ini
    active_keys = set()

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get('type')

                # Update nama perangkat jika dikirim dari client
                if data.get('device_name'):
                    device_label = str(data.get('device_name'))

                if msg_type == 'ping':
                    pong_payload = {'type': 'pong', 'caps_lock': is_caps_lock_on()}
                    if 't' in data:
                        pong_payload['t'] = data['t']
                    await ws.send_str(json.dumps(pong_payload))
                    continue

                elif msg_type == 'takeover':
                    continue

                # ── Handler Otentikasi & Pairing Perangkat ──
                elif msg_type == 'auth':
                    token = data.get('token', '')
                    dev_name = data.get('device_name') or device_label
                    if pairing_manager.is_authorized(token, client_ip):
                        is_client_authorized = True
                        client_token = token
                        await ws.send_str(json.dumps({
                            'type': 'auth_status',
                            'authorized': True,
                            'token': token,
                            'device_name': dev_name,
                            'license': license_manager.get_info()
                        }))
                        await ws.send_str(json.dumps({
                            'type': 'controller_status',
                            'role': 'active',
                            'message': 'Perangkat terhubung sebagai Pengendali PC.'
                        }))
                    else:
                        is_client_authorized = False
                        await ws.send_str(json.dumps({
                            'type': 'auth_status',
                            'authorized': False,
                            'reason': 'pairing_required',
                            'pin_required': True,
                            'host_name': socket.gethostname(),
                            'license': license_manager.get_info()
                        }))
                    continue

                elif msg_type == 'pair_request':
                    pin = data.get('pin', '')
                    dev_name = data.get('device_name') or device_label
                    token, msg_str = pairing_manager.verify_and_register(pin, dev_name, client_ip, ua)
                    if token:
                        is_client_authorized = True
                        client_token = token
                        await ws.send_str(json.dumps({
                            'type': 'pairing_result',
                            'success': True,
                            'token': token,
                            'device_name': dev_name,
                            'message': msg_str,
                            'license': license_manager.get_info()
                        }))
                        await ws.send_str(json.dumps({
                            'type': 'controller_status',
                            'role': 'active',
                            'message': 'Perangkat terhubung sebagai Pengendali PC.'
                        }))
                        print(f"[PAIR] Perangkat ter-pairing: {dev_name} ({client_ip})")
                    else:
                        await ws.send_str(json.dumps({
                            'type': 'pairing_result',
                            'success': False,
                            'message': msg_str
                        }))
                    continue

                elif msg_type == 'get_pairing_info':
                    await ws.send_str(json.dumps({
                        'type': 'pairing_info',
                        'pin': pairing_manager.get_or_create_pin(),
                        'devices': pairing_manager.get_paired_list()
                    }))
                    continue

                elif msg_type == 'unpair_device':
                    dev_id = data.get('device_id') or data.get('token_prefix')
                    if dev_id:
                        pairing_manager.unpair_device(dev_id)
                        await ws.send_str(json.dumps({
                            'type': 'pairing_info',
                            'pin': pairing_manager.get_or_create_pin(),
                            'devices': pairing_manager.get_paired_list()
                        }))
                    continue

                elif msg_type == 'activate_license':
                    key_str = data.get('key', '')
                    email = data.get('email', '')
                    ok, act_msg = license_manager.activate_key(key_str, email)
                    lic_info = license_manager.get_info()
                    await ws.send_str(json.dumps({
                        'type': 'license_activation_result',
                        'success': ok,
                        'message': act_msg,
                        'license': lic_info
                    }))
                    if ok:
                        bcast = json.dumps({'type': 'license_update', 'license': lic_info})
                        for c in list(CONNECTED_CLIENTS):
                            try:
                                await c.send_str(bcast)
                            except Exception:
                                pass
                    continue

                # ── Proteksi Pairing: Blokir input kontrol jika perangkat belum ter-pairing ──
                if not is_client_authorized and pairing_manager.pairing_enabled:
                    if not pairing_manager.is_authorized(client_token, client_ip):
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'code': 'UNAUTHORIZED',
                            'message': 'Perangkat belum di-pairing dengan PC host. Silakan masukkan PIN.'
                        }))
                        continue

                if msg_type == 'keypress':
                    key_name = data.get('key')
                    char = data.get('char')
                    mods = data.get('modifiers', {})

                    target = resolve_key(key_name) if key_name else char

                    # Tekan modifier jika ada dan belum aktif ditekan secara persisten
                    applied_mods = []
                    if mods.get('ctrl') and 'ctrl' not in active_keys and resolve_key('ctrl') not in active_keys:
                        simulate_press('ctrl')
                        applied_mods.append('ctrl')
                    if mods.get('alt') and 'alt' not in active_keys and resolve_key('alt') not in active_keys:
                        simulate_press('alt')
                        applied_mods.append('alt')
                    if mods.get('shift') and not char and 'shift' not in active_keys and resolve_key('shift') not in active_keys:
                        # Shift untuk special key
                        simulate_press('shift')
                        applied_mods.append('shift')
                    if mods.get('cmd') and 'cmd' not in active_keys and resolve_key('cmd') not in active_keys:
                        simulate_press('cmd')
                        applied_mods.append('cmd')

                    # Kirim tombol utama
                    if target:
                        simulate_tap(target)
                        if key_name == 'caps_lock':
                            await asyncio.sleep(0.05)
                            curr_caps = is_caps_lock_on()
                            for cws in list(CONNECTED_CLIENTS):
                                try:
                                    await cws.send_str(json.dumps({
                                        'type': 'caps_state',
                                        'caps_lock': curr_caps
                                    }))
                                except Exception:
                                    pass

                    # Lepas hanya modifier sementara yang ditekan khusus untuk keypress ini
                    for m in reversed(applied_mods):
                        simulate_release(m)

                elif msg_type == 'keydown':
                    key_name = data.get('key')
                    target = resolve_key(key_name)
                    if target:
                        simulate_press(target)
                        active_keys.add(key_name)
                        active_keys.add(target)
                        ACTIVE_KEYS.add(key_name)
                        ACTIVE_KEYS.add(target)

                elif msg_type == 'keyup':
                    key_name = data.get('key')
                    target = resolve_key(key_name)
                    if target:
                        simulate_release(target)
                        active_keys.discard(key_name)
                        active_keys.discard(target)
                        ACTIVE_KEYS.discard(key_name)
                        ACTIVE_KEYS.discard(target)

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

                elif msg_type == 'mouseabs':
                    rx = data.get('x', 0)
                    ry = data.get('y', 0)
                    simulate_mouse_abs(rx, ry)

                elif msg_type == 'volume_set':
                    val = data.get('value', 50)
                    set_system_volume(val)

                elif msg_type == 'mousescroll':
                    dx = data.get('dx', 0)
                    dy = data.get('dy', 0)
                    simulate_mouse_scroll(dx, dy)

                elif msg_type == 'type_text':
                    text_content = data.get('text', '')
                    if text_content:
                        if KEYBOARD_AVAILABLE and keyboard_controller and not UINPUT_AVAILABLE:
                            try:
                                keyboard_controller.type(text_content)
                            except Exception:
                                for ch in text_content:
                                    simulate_tap(ch)
                                    await asyncio.sleep(0.003)
                        else:
                            for ch in text_content:
                                simulate_tap(ch)
                                await asyncio.sleep(0.003)

                elif msg_type == 'get_window_list':
                    windows = await asyncio.to_thread(get_open_windows_list)
                    try:
                        await ws.send_str(json.dumps({
                            'type': 'window_list',
                            'windows': windows
                        }))
                    except Exception:
                        pass

                elif msg_type == 'control_window':
                    win_id = data.get('win_id')
                    action = data.get('action')
                    if win_id and action:
                        if action == 'minimize':
                            await asyncio.to_thread(minimize_window, win_id)
                        elif action == 'maximize':
                            await asyncio.to_thread(maximize_window, win_id)
                        elif action == 'close':
                            await asyncio.to_thread(close_window, win_id)
                        elif action == 'activate':
                            maximize = data.get('maximize', False)
                            await asyncio.to_thread(activate_and_focus_window, win_id, maximize)

                        # Jeda singkat agar OS Window Manager menyelesaikan perubahan state
                        await asyncio.sleep(0.18)
                        new_info = await asyncio.to_thread(get_active_window_info)
                        if new_info:
                            CURRENT_APP_CONTEXT = new_info
                            broadcast_payload = json.dumps({
                                'type': 'app_context',
                                'app': new_info['app'],
                                'title': new_info['title'],
                                'suggested_mode': new_info['suggested_mode'],
                                'class_name': new_info['class_name']
                            })
                            for client in list(CONNECTED_CLIENTS):
                                try:
                                    await client.send_str(broadcast_payload)
                                except Exception:
                                    pass

                        # Siarkan daftar jendela terbaru ke semua client aktif
                        windows = await asyncio.to_thread(get_open_windows_list)
                        list_payload = json.dumps({
                            'type': 'window_list',
                            'windows': windows
                        })
                        for client in list(CONNECTED_CLIENTS):
                            try:
                                await client.send_str(list_payload)
                            except Exception:
                                pass

                elif msg_type == 'activate_window':
                    win_id = data.get('win_id')
                    maximize = data.get('maximize', True)
                    if win_id:
                        await asyncio.to_thread(activate_and_focus_window, win_id, maximize)
                        # Segera periksa dan siarkan konteks aplikasi aktif yang baru
                        new_info = await asyncio.to_thread(get_active_window_info)
                        if new_info:
                            CURRENT_APP_CONTEXT = new_info
                            broadcast_payload = json.dumps({
                                'type': 'app_context',
                                'app': new_info['app'],
                                'title': new_info['title'],
                                'suggested_mode': new_info['suggested_mode'],
                                'class_name': new_info['class_name']
                            })
                            for client in list(CONNECTED_CLIENTS):
                                try:
                                    await client.send_str(broadcast_payload)
                                except Exception:
                                    pass

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[!] WS Error: {ws.exception()}")

    finally:
        CONNECTED_CLIENTS.discard(ws)
        # Lepaskan semua tombol yang masih tertahan jika koneksi terputus
        release_all_client_keys(active_keys)
        if MOUSE_AVAILABLE and mouse_controller and MouseButton:
            try:
                mouse_controller.release(MouseButton.left)
                mouse_controller.release(MouseButton.right)
            except Exception:
                pass
        print(f"[-] Client terputus: {client_ip} | {device_label} (Sisa terhubung: {len(CONNECTED_CLIENTS)})")

    return ws


# --- HTTP Index Handler ---
async def index_handler(request):
    static_dir = os.path.join(BASE_DIR, 'static')
    return web.FileResponse(os.path.join(static_dir, 'index.html'))


def print_banner(ports, ips):
    if isinstance(ports, int):
        ports = [ports]
    port = ports[0]
    primary_url = f"http://{ips[0]}:{port}"
    print("=" * 60)
    print(f"  REMOTE PC KEYBOARD SERVER v{__version__}")
    print("=" * 60)
    print("Buka browser di HP/Tablet Anda yang terhubung ke Wi-Fi yang sama:")
    for ip in ips:
        print(f"  http://{ip}:{port}")
    print("-" * 60)
    print("KONEKSI KABEL USB (Ultra-Low Latency <1ms):")
    print(f"  http://localhost:{port}")
    print("-" * 60)

    cur_pin = pairing_manager.get_or_create_pin()
    lic_info = license_manager.get_info()
    formatted_pin = f"{cur_pin[:3]} {cur_pin[3:]}" if len(cur_pin) == 6 else cur_pin
    print(f"KODE PIN PAIRING PERANGKAT: [ {formatted_pin} ]")
    print("Masukkan 6 digit PIN di atas pada HP Anda saat pertama kali menyambung.")
    print(f"STATUS LISENSI SAAS: {lic_info['plan_name']} | Status: {lic_info['status'].upper()}")
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


async def adb_reverse_watcher(ports):
    """Mendeteksi perangkat Android via kabel USB dan otomatis mengaktifkan port reverse forwarding (<1ms)"""
    if isinstance(ports, int):
        ports = [ports]
    adb_cmd = shutil.which('adb')
    if not adb_cmd:
        return
    known_devices = set()
    while True:
        try:
            proc = await asyncio.create_subprocess_exec(
                adb_cmd, 'devices',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            lines = stdout.decode().strip().splitlines()[1:]
            current_devices = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'device':
                    current_devices.add(parts[0])

            new_devices = current_devices - known_devices
            for dev in new_devices:
                for p in ports:
                    r_proc = await asyncio.create_subprocess_exec(
                        adb_cmd, '-s', dev, 'reverse', f'tcp:{p}', f'tcp:{p}',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await r_proc.communicate()
                print(f"[USB] Terdeteksi kabel USB terhubung: {dev} -> Port reverse aktif ({', '.join(str(p) for p in ports)})")

            known_devices = current_devices
        except Exception:
            pass
        await asyncio.sleep(4.0)


async def start_background_tasks(app):
    ports = app.get('server_ports', [8080])
    app['adb_watcher_task'] = asyncio.create_task(adb_reverse_watcher(ports))


async def cleanup_background_tasks(app):
    if 'adb_watcher_task' in app:
        app['adb_watcher_task'].cancel()
        try:
            await app['adb_watcher_task']
        except asyncio.CancelledError:
            pass


async def api_version_handler(request):
    return web.json_response(
        {'version': __version__, 'name': 'DigiKeyboard', 'hostname': socket.gethostname()},
        headers={'Access-Control-Allow-Origin': '*'}
    )


async def api_info_handler(request):
    return web.json_response({
        'version': __version__,
        'name': 'DigiKeyboard',
        'hostname': socket.gethostname(),
        'host_os': get_host_os(),
        'platform': sys.platform,
        'uinput_active': UINPUT_AVAILABLE
    }, headers={'Access-Control-Allow-Origin': '*'})


async def options_handler(request):
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': '*'
    })


def create_app(ports=[8080]):
    app = web.Application()
    app['server_ports'] = ports
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    static_dir = os.path.join(BASE_DIR, 'static')

    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_get('/api/version', api_version_handler)
    app.router.add_options('/api/version', options_handler)
    app.router.add_get('/api/info', api_info_handler)
    app.router.add_options('/api/info', options_handler)
    app.router.add_get('/api/license', lambda r: web.json_response(license_manager.get_info(), headers={'Access-Control-Allow-Origin': '*'}))
    app.router.add_get('/api/pairing/pin', lambda r: web.json_response({'pin': pairing_manager.get_or_create_pin()}, headers={'Access-Control-Allow-Origin': '*'}))
    app.router.add_static('/static/', path=static_dir, name='static')
    # Juga route langsung untuk style.css, app.js, manifest.json, sw.js, dan favicon jika diminta di root
    app.router.add_get('/style.css', lambda r: web.FileResponse(os.path.join(static_dir, 'style.css')))
    app.router.add_get('/app.js', lambda r: web.FileResponse(os.path.join(static_dir, 'app.js')))
    app.router.add_get('/manifest.json', lambda r: web.FileResponse(os.path.join(static_dir, 'manifest.json'), headers={'Content-Type': 'application/manifest+json'}))
    app.router.add_get('/sw.js', lambda r: web.FileResponse(os.path.join(static_dir, 'sw.js'), headers={'Content-Type': 'application/javascript'}))
    app.router.add_get('/favicon.ico', lambda r: web.FileResponse(os.path.join(static_dir, 'icon-192.png')))
    # Route unduh langsung Android APK
    apk_file = os.path.join(static_dir, 'DigiKeyboard.apk')
    if os.path.exists(apk_file):
        app.router.add_get('/download/apk', lambda r: web.FileResponse(apk_file, headers={'Content-Disposition': 'attachment; filename="DigiKeyboard.apk"'}))
        app.router.add_get('/DigiKeyboard.apk', lambda r: web.FileResponse(apk_file, headers={'Content-Disposition': 'attachment; filename="DigiKeyboard.apk"'}))
    return app


if __name__ == '__main__':
    ports = [8080]
    env_port = os.environ.get('PORT')
    if env_port:
        try:
            ports = [int(env_port)]
        except ValueError:
            pass

    ips = get_local_ip_addresses()
    print_banner(ports, ips)

    app = create_app(ports)

    async def run_server():
        runner = web.AppRunner(app)
        await runner.setup()
        for p in ports:
            site = web.TCPSite(runner, '0.0.0.0', p)
            await site.start()
        print(f"[OK] Server aktif di port {', '.join(str(p) for p in ports)}.")

        context_task = asyncio.create_task(smart_context_tracker_loop())

        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        import signal
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop_event.set)
            except (NotImplementedError, RuntimeError):
                pass

        await stop_event.wait()
        print("\n[*] Mematikan server secara aman...")
        context_task.cancel()
        try:
            await context_task
        except asyncio.CancelledError:
            pass
        await runner.cleanup()

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n[*] Server dihentikan oleh pengguna.")
    except OSError as e:
        if getattr(e, 'errno', None) in (98, 10048):  # Linux 98, Windows 10048
            print(f"\n[!] Port sedang digunakan oleh program lain: {e}")
        else:
            print(f"\n[!] Gagal menjalankan server: {e}")
        sys.exit(1)
