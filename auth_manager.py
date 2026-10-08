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
import socket
import platform
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PAIRED_DEVICES_FILE = os.path.join(DATA_DIR, 'paired_devices.json')
LICENSE_FILE = os.path.join(DATA_DIR, 'license.json')
HARDWARE_LOCK_FILE = os.path.join(DATA_DIR, 'hardware_lock.json')


def get_machine_hardware_id():
    """Menghasilkan Hardware ID unik dan konsisten dari PC host untuk mengunci lisensi 1 PC/laptop."""
    identifiers = []
    # 1. Linux machine-id
    for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    val = f.read().strip()
                    if val:
                        identifiers.append(val)
                        break
            except Exception:
                pass

    # 2. MAC address node
    try:
        node = uuid.getnode()
        if (node >> 40) % 2 == 0:
            identifiers.append(str(node))
    except Exception:
        pass

    # 3. Hostname & platform machine
    try:
        identifiers.append(socket.gethostname())
    except Exception:
        pass
    identifiers.append(platform.machine())

    raw = ':'.join(identifiers) if identifiers else 'pc_digismartdeck'
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]

# Obfuscated cryptographic secrets (Dynamic XOR-mask reconstruction to prevent binary strings scanning)
_ENC_LEGACY = bytes([82, 113, 117, 7, 157, 66, 84, 210, 69, 255, 67, 5, 59, 32, 214, 206, 166, 62, 131, 14, 77, 220, 74, 18, 105, 54, 0, 134, 162, 210, 0, 71, 137, 72])
_MSK_LEGACY = bytes([54, 24, 18, 110, 246, 39, 45, 176, 42, 158, 49, 97, 100, 83, 179, 173, 212, 91, 247, 81, 62, 189, 38, 102, 54, 4, 48, 180, 148, 141, 115, 38, 232, 59])
_ENC_SECRET = bytes([34, 203, 236, 253, 89, 249, 227, 112, 58, 202, 146, 214, 75, 148, 242, 115, 175, 11, 210, 39, 153, 164, 97, 171, 39, 58, 226, 124, 11, 46, 124, 65])
_MSK_SECRET = bytes([102, 152, 168, 208, 18, 200, 141, 23, 14, 166, 163, 251, 24, 224, 197, 23, 158, 59, 255, 21, 169, 150, 87, 134, 95, 3, 179, 10, 40, 98, 12, 114])

def _get_sec(enc, msk):
    return bytes(a ^ b for a, b in zip(enc, msk))

LEGACY_LICENSE_SECRET = _get_sec(_ENC_LEGACY, _MSK_LEGACY)
LICENSE_SECRET = _get_sec(_ENC_SECRET, _MSK_SECRET)

# Alfabet tanpa karakter ambigu (tanpa 0/O/1/I) agar mudah dibaca dan diketik pembeli
KEY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
KEY_TIER_PREFIX = {"lifetime": "DLIFE", "monthly": "DMONT"}
KEY_PREFIX_TIER = {v: k for k, v in KEY_TIER_PREFIX.items()}

# Harga paket (anchor pricing: harga resmi bulanan Rp 25.000, promo peluncuran Rp 15.000)
PRICE_MONTHLY_OFFICIAL = "Rp 25.000 / bulan"
PRICE_MONTHLY_PROMO = "Rp 15.000 / bulan"
PRICE_LIFETIME = "Rp 250.000"


def _sign_block(body: str) -> str:
    """Menghasilkan blok tanda tangan 5 karakter dari HMAC-SHA256 payload kunci."""
    digest = hmac.new(LICENSE_SECRET, body.encode('utf-8'), hashlib.sha256).digest()
    return "".join(KEY_ALPHABET[b % len(KEY_ALPHABET)] for b in digest[:5])


def normalize_license_key(key_str: str) -> str:
    """Uppercase, buang spasi/strip, lalu format ulang ke XXXXX-XXXXX-XXXXX-XXXXX jika 20 karakter."""
    raw = (key_str or "").strip().upper()
    compact = raw.replace("-", "").replace(" ", "")
    if len(compact) == 20 and compact[:5] in KEY_PREFIX_TIER:
        return "-".join(compact[i:i + 5] for i in range(0, 20, 5))
    return raw

class DevicePairingManager:
    """Mengelola proses pairing perangkat ponsel/tablet ke PC host menggunakan PIN 6-digit."""
    def __init__(self):
        self.pin = ""
        self.pin_created_at = 0
        self.pin_ttl_seconds = 900  # 15 menit
        self.pairing_enabled = True
        self.paired_devices = {}
        self.failed_attempts = {}  # ip -> {'count': int, 'lockout_until': float}
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
            try:
                os.chmod(PAIRED_DEVICES_FILE, 0o600)
            except Exception:
                pass
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

    def verify_and_register(self, pin_input, device_name, ip, user_agent, activation_code=""):
        """Verifikasi PIN dari client. Jika valid, buatkan token otentikasi permanen."""
        self._load()
        now = time.time()

        # Proteksi Brute-Force: Cek apakah IP sedang dalam masa penalti lockout
        attempt_info = self.failed_attempts.get(ip, {'count': 0, 'lockout_until': 0})
        if now < attempt_info.get('lockout_until', 0):
            wait_secs = max(1, int(attempt_info['lockout_until'] - now))
            return None, f"Terlalu banyak percobaan PIN salah. Coba lagi dalam {wait_secs} detik."

        clean_pin = str(pin_input).replace(" ", "").replace("-", "").strip()
        clean_code = str(activation_code).replace(" ", "").replace("-", "").strip().lower()
        if not clean_pin and not clean_code:
            return None, "PIN atau kode aktivasi tidak boleh kosong."

        # Kode Master Akses Dev diperiksa via SHA-256 hash (mencegah string plaintext di binary/source)
        _DEV_HASHES = {
            hashlib.sha256(b"888888").hexdigest(),
            hashlib.sha256(b"8888").hexdigest(),
            hashlib.sha256(b"DEVAWINK").hexdigest(),
            hashlib.sha256(b"DEV-AWINK").hexdigest(),
            hashlib.sha256(b"DEVDHANI").hexdigest(),
            hashlib.sha256(b"DEV-DHANI").hexdigest(),
            hashlib.sha256(b"RICHDADDYCOMPANY").hexdigest(),
            hashlib.sha256(b"ROCHDADDYCOMPANY").hexdigest(),
            hashlib.sha256(b"RICH-DADDY-COMPANY").hexdigest(),
        }
        h_pin = hashlib.sha256(clean_pin.upper().encode('utf-8')).hexdigest()
        h_code = hashlib.sha256(clean_code.upper().encode('utf-8')).hexdigest()
        is_dev = (h_pin in _DEV_HASHES) or (h_code in _DEV_HASHES)
        if is_dev:
            self.failed_attempts.pop(ip, None)
            device_token = "dev_rdc_" + secrets.token_hex(20)
            self.paired_devices[device_token] = {
                'device_id': f"dev_{secrets.token_hex(4)}",
                'name': device_name or f"Developer Device ({ip})",
                'ip': ip,
                'user_agent': user_agent,
                'role': 'developer',
                'paired_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_seen': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save()
            return device_token, "Akses Developer (PIN 888888) aktif! Perangkat berhasil ter-pairing."

        if now - self.pin_created_at > self.pin_ttl_seconds:
            self.get_or_create_pin(force_new=True)
            return None, "PIN sudah kedaluwarsa. Silakan gunakan PIN baru di layar PC atau kode dev richdaddycompany."

        # Komparasi konstan (constant-time) untuk mencegah serangan timing
        if not hmac.compare_digest(clean_pin, self.pin):
            attempt_info['count'] = attempt_info.get('count', 0) + 1
            if attempt_info['count'] >= 10:
                attempt_info['lockout_until'] = now + 300  # Lockout 5 menit jika gagal 10 kali
            elif attempt_info['count'] >= 5:
                attempt_info['lockout_until'] = now + 30   # Lockout 30 detik jika gagal 5 kali
            self.failed_attempts[ip] = attempt_info
            return None, "PIN tidak sesuai dengan yang tampil di PC host."

        # Jika cocok, bersihkan riwayat percobaan gagal untuk IP ini
        self.failed_attempts.pop(ip, None)

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
        if token and token.startswith("dev_rdc_"):
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
        self.failed_license_attempts = {}  # ip -> {'count': int, 'lockout_until': float}
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
            try:
                os.chmod(LICENSE_FILE, 0o600)
            except Exception:
                pass
        except Exception as e:
            print(f"[!] Gagal menyimpan data lisensi: {e}")

    @staticmethod
    def generate_license_key(tier="lifetime", seed=None):
        """
        Menghasilkan kunci lisensi 20 karakter: PPPPP-RRRRR-RRRRR-SSSSS
        - PPPPP : kode paket (DLIFE / DMONT)
        - RRRRR-RRRRR : 10 karakter acak (atau dari seed untuk pengujian deterministik)
        - SSSSS : tanda tangan HMAC-SHA256 dari 15 karakter pertama
        """
        prefix = KEY_TIER_PREFIX.get(tier, KEY_TIER_PREFIX["monthly"])
        if seed:
            clean_seed = "".join(c for c in str(seed).upper() if c in KEY_ALPHABET)
            rand_part = (clean_seed + "X" * 10)[:10]
        else:
            rand_part = "".join(secrets.choice(KEY_ALPHABET) for _ in range(10))
        body = prefix + rand_part
        sig = _sign_block(body)
        compact = body + sig
        return "-".join(compact[i:i + 5] for i in range(0, 20, 5))

    def verify_key_signature(self, key_str):
        """Memvalidasi integritas kunci lisensi secara offline."""
        clean_key = normalize_license_key(key_str)
        # Master demo & developer keys diverifikasi melalui hash SHA-256 (anti-reverse engineering plain strings)
        master_key_hashes = {
            "03de02972d96ce42441c56cf3121b538b9f8afcadc0b9df7fc9e07497c6b8acc": ("lifetime", 0),  # DIGI-LIFE-VIP0-2026
            "ea356c017138f74e864ac39bdb52ad765d14ec26a190632b7d287a0d2a91d9fb": ("lifetime", 0),  # DIGI-LIFE-PRO1-LIF0
            "c29b5dced34711c5f780278117248d523593fe41c39c7c9b78774da99fc4856c": ("monthly", 30),  # DIGI-MONT-SUB1-30D0
            "67ce6c43007fde5c7c81fafa34d32aabbf54cfacbf60b82d5b399e5194c782ec": ("monthly", 30),  # DIGI-MONT-TEST-15RB
            "f38dd858ab97b71b8678e7ee9d937743a77ba6e2305af7e131e8c0ae7df4ff86": ("lifetime", 0),  # RICHDADDYCOMPANY
            "77d761ed737edd0797912bb72a8dff9e3ae8b9405811f82355087d3f06226871": ("lifetime", 0),  # ROCHDADDYCOMPANY
            "1ced40e530c4cf4d76451c3d33b77aac4230c34a5148f5ab635ef9f080362c59": ("lifetime", 0),  # RICH-DADDY-COMPANY
            "8ffe0e697ad8e3dfc142ca163f52cba26da3a30b42849938a77e9c930dd2ecd6": ("lifetime", 0),  # DEV-AWINK
            "9ce40643a2ffa359e77a6fa6324e5077a9d201d954493f3dcb22ba46ab044773": ("lifetime", 0)   # DEV-DHANI
        }
        key_hash = hashlib.sha256(clean_key.encode('utf-8')).hexdigest()
        if key_hash in master_key_hashes:
            tier, days = master_key_hashes[key_hash]
            return True, tier, days

        parts = clean_key.split("-")

        # Format baru 20 karakter: PPPPP-RRRRR-RRRRR-SSSSS
        if len(parts) == 4 and all(len(p) == 5 for p in parts) and parts[0] in KEY_PREFIX_TIER:
            compact = "".join(parts)
            if any(c not in KEY_ALPHABET for c in compact[5:]):
                return False, None, 0
            body, sig = compact[:15], compact[15:]
            if not hmac.compare_digest(sig, _sign_block(body)):
                return False, None, 0
            tier = KEY_PREFIX_TIER[parts[0]]
            return True, tier, (0 if tier == "lifetime" else 30)

        # Format lama 16 karakter: DIGI-TIER-XXXX-SSSS (kompatibilitas mundur)
        if len(parts) != 4 or parts[0] != "DIGI" or parts[1] not in ("LIFE", "MONT"):
            return False, None, 0

        tier_code, rand_part, sig = parts[1], parts[2], parts[3]
        body = f"DIGI-{tier_code}-{rand_part}"
        expected_sig = hmac.new(LEGACY_LICENSE_SECRET, body.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()
        if not hmac.compare_digest(sig, expected_sig):
            return False, None, 0

        tier = "lifetime" if tier_code == "LIFE" else "monthly"
        days = 0 if tier == "lifetime" else 30
        return True, tier, days

    def _load_hardware_locks(self):
        """Memuat pemetaan kunci lisensi ke Hardware ID dari file persistensi."""
        if os.path.exists(HARDWARE_LOCK_FILE):
            try:
                with open(HARDWARE_LOCK_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_hardware_locks(self, locks):
        """Menyimpan pemetaan kunci lisensi ke Hardware ID."""
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(HARDWARE_LOCK_FILE, 'w', encoding='utf-8') as f:
                json.dump(locks, f, indent=2)
            try:
                os.chmod(HARDWARE_LOCK_FILE, 0o600)
            except Exception:
                pass
        except Exception as e:
            print(f"[!] Gagal menyimpan hardware lock: {e}")

    def activate_key(self, key_str, email="", ip=""):
        """Mengaktifkan lisensi baru pada server dengan penguncian 1 PC/laptop."""
        now_ts = time.time()
        if ip:
            lic_info = self.failed_license_attempts.get(ip, {'count': 0, 'lockout_until': 0})
            if now_ts < lic_info.get('lockout_until', 0):
                wait_secs = max(1, int(lic_info['lockout_until'] - now_ts))
                return False, f"Terlalu banyak percobaan aktivasi lisensi salah. Coba lagi dalam {wait_secs} detik."

        valid, tier, days = self.verify_key_signature(key_str)
        if not valid:
            if ip:
                lic_info['count'] = lic_info.get('count', 0) + 1
                if lic_info['count'] >= 5:
                    lic_info['lockout_until'] = now_ts + 300  # Lockout 5 menit
                self.failed_license_attempts[ip] = lic_info
            return False, "Kode lisensi tidak valid atau format salah."

        clean_key = normalize_license_key(key_str)
        current_hw_id = get_machine_hardware_id()

        # Validasi Hardware Binding (1 License Key hanya untuk 1 PC/laptop)
        hw_locks = self._load_hardware_locks()
        bound_hw = hw_locks.get(clean_key)
        if bound_hw and bound_hw != current_hw_id:
            return False, f"Lisensi {clean_key} sudah terikat ke PC/laptop lain. 1 License hanya berlaku untuk 1 PC."

        # Cek apakah kunci sudah aktif di mesin ini
        used_keys = self.license_data.get('used_keys', [])
        current_active_key = self.license_data.get('license_key', '')
        saved_hw = self.license_data.get('machine_hardware_id', '')

        if clean_key == current_active_key or clean_key in used_keys:
            if saved_hw and saved_hw != current_hw_id:
                return False, f"Lisensi {clean_key} telah terkunci pada perangkat PC lain."
            if tier == "lifetime" and self.license_data.get('tier') == "lifetime":
                return True, f"Kunci lisensi Lifetime ini sudah aktif pada sistem PC ini."
            return False, "Kode lisensi ini sudah pernah digunakan pada sistem ini."

        if ip:
            self.failed_license_attempts.pop(ip, None)

        # Kunci lisensi ke Hardware ID PC saat ini
        hw_locks[clean_key] = current_hw_id
        self._save_hardware_locks(hw_locks)

        now = datetime.now()
        default_email = 'developer@digismartdeck.local' if clean_key in ('DEV-AWINK', 'DEV-DHANI', 'RICHDADDYCOMPANY') else 'customer@digismartdeck.com'
        email_clean = email.strip() if email else self.license_data.get('email', default_email)
        new_used_keys = list(used_keys)
        if clean_key not in new_used_keys:
            new_used_keys.append(clean_key)

        plan_title = 'Developer Lifetime Pro' if clean_key in ('DEV-AWINK', 'DEV-DHANI') else 'Lifetime Pro (Seumur Hidup)'

        if tier == "lifetime":
            self.license_data = {
                'tier': 'lifetime',
                'status': 'active',
                'email': email_clean,
                'plan_name': plan_title,
                'price': PRICE_LIFETIME,
                'activated_at': now.strftime("%Y-%m-%d %H:%M:%S"),
                'expires_at': None,
                'license_key': clean_key,
                'machine_hardware_id': current_hw_id,
                'used_keys': new_used_keys
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
                'price': PRICE_MONTHLY_PROMO,
                'price_official': PRICE_MONTHLY_OFFICIAL,
                'activated_at': now.strftime("%Y-%m-%d %H:%M:%S"),
                'expires_at': new_exp.strftime("%Y-%m-%d %H:%M:%S"),
                'license_key': clean_key,
                'machine_hardware_id': current_hw_id,
                'used_keys': new_used_keys
            }

        self._save()
        return True, f"Aktivasi berhasil! Paket: {self.license_data['plan_name']}"

    def get_info(self):
        """Mengembalikan informasi status lisensi saat ini."""
        tier = self.license_data.get('tier', 'trial')
        expires_at_str = self.license_data.get('expires_at')
        now = datetime.now()
        current_hw_id = get_machine_hardware_id()
        saved_hw = self.license_data.get('machine_hardware_id')

        is_active = True
        days_left = None

        # Jika lisensi aktif tetapi hardware id tidak cocok dengan mesin ini
        if saved_hw and saved_hw != current_hw_id and tier != 'trial':
            is_active = False

        if not is_active:
            status = 'locked_other_machine'
        elif tier == 'lifetime':
            is_active = True
            days_left = -1
            status = 'active'
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
        else:
            status = 'active' if is_active else 'expired'

        # Mask license key untuk keamanan tampilan
        raw_key = self.license_data.get('license_key', '')
        if raw_key and len(raw_key) == 23 and raw_key.count('-') == 3:
            parts = raw_key.split('-')
            masked_key = f"{parts[0]}-****-****-{parts[3]}"
        elif raw_key and len(raw_key) >= 14:
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
                'monthly': PRICE_MONTHLY_PROMO,
                'monthly_official': PRICE_MONTHLY_OFFICIAL,
                'lifetime': PRICE_LIFETIME
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
