#!/usr/bin/env python3
"""
DigiSmartDeck Authentication & Licensing Manager
Modul untuk menangani:
1. Pairing Perangkat Aman (PIN 6-Digit & Whitelist Token Perangkat)
2. Sistem Lisensi Komersial SaaS (Free Trial, Langganan Bulanan Rp 15rb, Lisensi Lifetime Rp 250rb)
"""

import os
import json
import time
import uuid
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PAIRED_DEVICES_FILE = os.path.join(DATA_DIR, 'paired_devices.json')
LICENSE_FILE = os.path.join(DATA_DIR, 'license.json')

LICENSE_SECRET = b"digikeyboard_secret_salt_2026_saas"

class DevicePairingManager:
    """Mengelola proses pairing perangkat ponsel/tablet ke PC host menggunakan PIN 6-digit."""
    def __init__(self):
        self.pin = ""
        self.pin_created_at = 0
        self.pin_ttl_seconds = 900  # 15 menit
        self.pairing_enabled = True
        self.paired_devices = {}
        self._load()
        self.get_or_create_pin()

    def _load(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(PAIRED_DEVICES_FILE):
            try:
                with open(PAIRED_DEVICES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pairing_enabled = data.get('pairing_enabled', True)
                    self.paired_devices = data.get('paired_devices', {})
                    saved_pin = data.get('current_pin')
                    saved_pin_time = data.get('pin_created_at', 0)
                    if saved_pin:
                        self.pin = str(saved_pin)
                        self.pin_created_at = float(saved_pin_time)
            except Exception as e:
                print(f"[!] Gagal memuat data pairing: {e}")
                self.paired_devices = {}

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(PAIRED_DEVICES_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'pairing_enabled': self.pairing_enabled,
                    'current_pin': self.pin,
                    'pin_created_at': self.pin_created_at,
                    'paired_devices': self.paired_devices
                }, f, indent=2)
        except Exception as e:
            print(f"[!] Gagal menyimpan data pairing: {e}")

    def get_or_create_pin(self, force_new=False):
        self._load()
        now = time.time()
        if force_new or not self.pin or (now - self.pin_created_at > self.pin_ttl_seconds):
            self.pin = f"{secrets.randbelow(900000) + 100000}"
            self.pin_created_at = now
            self._save()
        return self.pin

    def generate_pin(self):
        return self.get_or_create_pin(force_new=True)

    def verify_and_register(self, pin_input, device_name, ip, user_agent):
        """Verifikasi PIN dari client. Jika valid, buatkan token otentikasi permanen."""
        self._load()
        clean_pin = str(pin_input).replace(" ", "").replace("-", "").strip()
        if not clean_pin:
            return None, "PIN tidak boleh kosong."

        now = time.time()
        if now - self.pin_created_at > self.pin_ttl_seconds:
            self.get_or_create_pin(force_new=True)
            return None, "PIN sudah kedaluwarsa. Silakan gunakan PIN baru di layar PC."

        if clean_pin != self.pin:
            return None, "PIN tidak sesuai dengan yang tampil di PC host."

        # Buat token unik permanen untuk perangkat ini
        device_token = secrets.token_hex(24)
        self.paired_devices[device_token] = {
            'device_id': f"dev_{secrets.token_hex(4)}",
            'name': device_name or f"Device ({ip})",
            'ip': ip,
            'user_agent': user_agent,
            'paired_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_seen': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save()
        return device_token, "Pairing berhasil!"

    def is_authorized(self, token, ip=""):
        """Periksa apakah token perangkat sah dan terdaftar."""
        if not self.pairing_enabled:
            return True
        # Localhost (koneksi USB adb reverse atau browser di PC yang sama) otomatis diizinkan jika belum ada device
        if ip in ("127.0.0.1", "localhost", "::1") and not self.paired_devices:
            return True
        if not token or token not in self.paired_devices:
            return False
        # Update last seen
        self.paired_devices[token]['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def get_paired_list(self):
        """Ambil daftar perangkat terhubung tanpa membocorkan secret token."""
        result = []
        for token, info in self.paired_devices.items():
            result.append({
                'device_id': info.get('device_id'),
                'token_prefix': token[:6] + "...",
                'name': info.get('name'),
                'ip': info.get('ip'),
                'paired_at': info.get('paired_at'),
                'last_seen': info.get('last_seen')
            })
        return result

    def unpair_device(self, identifier):
        """Hapus perangkat berdasarkan prefix token atau device_id."""
        clean_id = identifier.rstrip('.') if identifier else ''
        to_del = []
        for token, info in self.paired_devices.items():
            if (clean_id and token.startswith(clean_id)) or info.get('device_id') == identifier:
                to_del.append(token)
        for t in to_del:
            del self.paired_devices[t]
        if to_del:
            self._save()
            return True
        return False

    def unpair_all(self):
        self.paired_devices.clear()
        self._save()
        self.get_or_create_pin(force_new=True)


class LicenseManager:
    """
    Mengelola lisensi SaaS komersial DigiSmartDeck:
    - Free Trial: 7 Hari Akses Penuh
    - Langganan Bulanan: Rp 25.000 / bulan
    - Lisensi Seumur Hidup: Rp 250.000 (Lifetime Pro)
    """
    def __init__(self):
        self.license_data = {}
        self._load()

    def _load(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
                    self.license_data = json.load(f)
            except Exception as e:
                print(f"[!] Gagal memuat data lisensi: {e}")
                self._init_default_trial()
        else:
            self._init_default_trial()

    def _init_default_trial(self):
        now = datetime.now()
        trial_days = 7
        expires = now + timedelta(days=trial_days)
        self.license_data = {
            'tier': 'trial',
            'status': 'active',
            'email': 'trial@digismartdeck.local',
            'plan_name': 'Free Trial (7 Hari)',
            'created_at': now.strftime("%Y-%m-%d %H:%M:%S"),
            'activated_at': now.strftime("%Y-%m-%d %H:%M:%S"),
            'expires_at': expires.strftime("%Y-%m-%d %H:%M:%S"),
            'license_key': 'DIGI-TRIA-FREE-0007'
        }
        self._save()

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.license_data, f, indent=2)
        except Exception as e:
            print(f"[!] Gagal menyimpan data lisensi: {e}")

    @staticmethod
    def generate_license_key(tier="lifetime", seed="VIP2026"):
        """Menghasilkan kunci lisensi sah dengan checksum HMAC deterministik."""
        tier_code = "LIFE" if tier == "lifetime" else "MONT"
        rand_part = seed[:4].upper().ljust(4, 'X')
        body = f"DIGI-{tier_code}-{rand_part}"
        sig = hmac.new(LICENSE_SECRET, body.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()
        return f"{body}-{sig}"

    def verify_key_signature(self, key_str):
        """Memvalidasi integritas kunci lisensi secara offline."""
        clean_key = key_str.strip().upper()
        # Master demo keys untuk pengujian lokal & evaluasi
        master_keys = {
            "DIGI-LIFE-VIP0-2026": ("lifetime", 0),
            "DIGI-LIFE-PRO1-LIF0": ("lifetime", 0),
            "DIGI-MONT-SUB1-30D0": ("monthly", 30),
            "DIGI-MONT-TEST-15RB": ("monthly", 30)
        }
        if clean_key in master_keys:
            tier, days = master_keys[clean_key]
            return True, tier, days

        parts = clean_key.split("-")
        if len(parts) != 4 or parts[0] != "DIGI":
            return False, None, 0

        tier_code, rand_part, sig = parts[1], parts[2], parts[3]
        body = f"DIGI-{tier_code}-{rand_part}"
        expected_sig = hmac.new(LICENSE_SECRET, body.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()
        if sig != expected_sig:
            return False, None, 0

        tier = "lifetime" if tier_code == "LIFE" else "monthly"
        days = 0 if tier == "lifetime" else 30
        return True, tier, days

    def activate_key(self, key_str, email=""):
        """Mengaktifkan lisensi baru pada server."""
        valid, tier, days = self.verify_key_signature(key_str)
        if not valid:
            return False, "Kode lisensi tidak valid atau format salah."

        now = datetime.now()
        email_clean = email.strip() if email else self.license_data.get('email', 'customer@digismartdeck.com')

        if tier == "lifetime":
            self.license_data = {
                'tier': 'lifetime',
                'status': 'active',
                'email': email_clean,
                'plan_name': 'Lifetime Pro (Seumur Hidup)',
                'price': 'Rp 250.000',
                'activated_at': now.strftime("%Y-%m-%d %H:%M:%S"),
                'expires_at': None,
                'license_key': key_str.strip().upper()
            }
        else:
            # Perpanjang jika masih aktif, atau mulai baru
            current_exp = None
            if self.license_data.get('tier') == 'monthly' and self.license_data.get('expires_at'):
                try:
                    exp_dt = datetime.strptime(self.license_data['expires_at'], "%Y-%m-%d %H:%M:%S")
                    if exp_dt > now:
                        current_exp = exp_dt
                except Exception:
                    pass

            start_point = current_exp if current_exp else now
            new_exp = start_point + timedelta(days=days or 30)

            self.license_data = {
                'tier': 'monthly',
                'status': 'active',
                'email': email_clean,
                'plan_name': 'Langganan Bulanan Pro',
                'price': 'Rp 25.000 / bln',
                'activated_at': now.strftime("%Y-%m-%d %H:%M:%S"),
                'expires_at': new_exp.strftime("%Y-%m-%d %H:%M:%S"),
                'license_key': key_str.strip().upper()
            }

        self._save()
        return True, f"Aktivasi berhasil! Paket: {self.license_data['plan_name']}"

    def get_info(self):
        """Mengembalikan informasi status lisensi saat ini."""
        tier = self.license_data.get('tier', 'trial')
        expires_at_str = self.license_data.get('expires_at')
        now = datetime.now()

        is_active = True
        days_left = None

        if tier == 'lifetime':
            is_active = True
            days_left = -1
        elif expires_at_str:
            try:
                exp_dt = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                delta = exp_dt - now
                days_left = max(0, delta.days)
                if delta.total_seconds() <= 0:
                    is_active = False
            except Exception:
                is_active = False

        status = 'active' if is_active else 'expired'

        # Mask license key untuk keamanan tampilan
        raw_key = self.license_data.get('license_key', '')
        if raw_key and len(raw_key) >= 14:
            masked_key = raw_key[:9] + "****-" + raw_key[-4:]
        else:
            masked_key = raw_key

        return {
            'tier': tier,
            'status': status,
            'plan_name': self.license_data.get('plan_name', 'Free Trial'),
            'email': self.license_data.get('email', ''),
            'license_key': masked_key,
            'activated_at': self.license_data.get('activated_at', ''),
            'expires_at': expires_at_str,
            'days_left': days_left,
            'pricing': {
                'monthly': 'Rp 25.000 / bulan',
                'lifetime': 'Rp 250.000 (Lifetime)'
            }
        }


# Instance Global
pairing_manager = DevicePairingManager()
license_manager = LicenseManager()

if __name__ == '__main__':
    print("[TEST] DevicePairingManager PIN:", pairing_manager.get_or_create_pin())
    print("[TEST] LicenseManager Info:", json.dumps(license_manager.get_info(), indent=2))
    sample_key = license_manager.generate_license_key("lifetime", "DEMO")
    print(f"[TEST] Generated sample key: {sample_key}")
    valid, t, d = license_manager.verify_key_signature(sample_key)
    print(f"[TEST] Key validation: valid={valid}, tier={t}, days={d}")
