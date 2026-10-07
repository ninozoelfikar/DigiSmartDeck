#!/usr/bin/env python3
"""
DigiSmartDeck - Batch License Key Generator
Menghasilkan batch kode lisensi 20 karakter alfanumerik (XXXXX-XXXXX-XXXXX-XXXXX)
dengan tanda tangan kriptografi HMAC-SHA256 offline untuk diimpor ke platform Mayar.id.

Penggunaan:
    python3 tools/generate_license_keys.py --tier monthly --count 100 --output data/keys_monthly.csv
    python3 tools/generate_license_keys.py --tier lifetime --count 50 --output data/keys_lifetime.csv
"""

import os
import sys
import argparse
import csv
from datetime import datetime

# Tambahkan root path ke sys.path agar bisa mengimpor auth_manager
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from auth_manager import license_manager, PRICE_LIFETIME, PRICE_MONTHLY_OFFICIAL, PRICE_MONTHLY_PROMO


def generate_batch(tier="monthly", count=100, output_file=None):
    if tier not in ("monthly", "lifetime"):
        print(f"[ERROR] Tier '{tier}' tidak valid. Pilihan: monthly, lifetime")
        sys.exit(1)

    plan_name = "Lifetime Pro" if tier == "lifetime" else "Langganan Bulanan Pro"
    price = PRICE_LIFETIME if tier == "lifetime" else f"{PRICE_MONTHLY_PROMO} (Resmi: {PRICE_MONTHLY_OFFICIAL})"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    keys = []
    seen = set()
    while len(keys) < count:
        key = license_manager.generate_license_key(tier=tier)
        if key in seen:
            continue
        valid, t, d = license_manager.verify_key_signature(key)
        if not valid or t != tier:
            continue
        seen.add(key)
        keys.append({
            "license_key": key,
            "tier": tier,
            "plan_name": plan_name,
            "price": price,
            "created_at": now_str
        })

    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["license_key", "tier", "plan_name", "price", "created_at"])
            writer.writeheader()
            writer.writerows(keys)
        print(f"[OK] Berhasil menghasilkan {len(keys)} kunci '{tier}' ke file: {output_file}")
    else:
        print(f"[INFO] {len(keys)} Kunci '{tier}':")
        for item in keys:
            print(item["license_key"])

    return keys


def main():
    parser = argparse.ArgumentParser(description="DigiSmartDeck Batch License Generator")
    parser.add_argument("--tier", choices=["monthly", "lifetime"], default="monthly", help="Tipe paket (monthly / lifetime)")
    parser.add_argument("--count", type=int, default=20, help="Jumlah kunci yang dihasilkan (default: 20)")
    parser.add_argument("--output", type=str, default=None, help="File output CSV tujuan (opsional)")

    args = parser.parse_args()
    generate_batch(tier=args.tier, count=args.count, output_file=args.output)


if __name__ == "__main__":
    main()
