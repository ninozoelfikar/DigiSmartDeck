#!/usr/bin/env python3
"""
Simulasi Mekanisme Auto-Updater DigiSmartDeck (Tablet/HP v1.21.0 -> v1.21.2)
Menguji:
1. Localhost / Local PC Server OTA Endpoint (/api/updater/check)
2. Fallback Endpoint (/api/version)
3. Skema GitHub Releases / Raw (Gratis tanpa biaya server)
4. Skema Firebase Remote Config / Hosting (Gratis tanpa biaya server)
"""

import argparse
import json
import os
import re
import sys


def parse_semver(ver_str):
    parts = [int(p) for p in re.findall(r'\d+', str(ver_str))]
    while len(parts) < 3:
        parts.append(0)
    code = parts[0] * 10000 + parts[1] * 100 + parts[2]
    return parts[:3], code


def simulate_local_server_check(client_ver, server_ver, apk_size_mb=6.3):
    client_parts, client_code = parse_semver(client_ver)
    server_parts, server_code = parse_semver(server_ver)

    update_available = (server_code > client_code) or (client_parts != server_parts)

    payload = {
        "status": "ok",
        "update_available": update_available,
        "current_server_version": server_ver,
        "server_version_code": server_code,
        "client_version": client_ver,
        "client_version_code": client_code,
        "download_url": f"/download/apk",
        "apk_filename": f"DigiSmartDeck-v{server_ver}.apk",
        "apk_size_mb": apk_size_mb,
        "changelog": f"Pembaruan otomatis dari v{client_ver} ke v{server_ver}"
    }
    return payload


def simulate_github_releases_check(client_ver, repo="ninozoelfikar/digikeyboard"):
    """
    Format manifest gratis via GitHub Releases API / raw json di repo:
    https://raw.githubusercontent.com/<owner>/<repo>/main/version.json
    atau
    https://api.github.com/repos/<owner>/<repo>/releases/latest
    """
    latest_tag = "v1.21.2"
    client_parts, client_code = parse_semver(client_ver)
    latest_parts, latest_code = parse_semver(latest_tag)

    update_available = latest_code > client_code

    manifest = {
        "source": "GitHub Releases",
        "repo": repo,
        "tag_name": latest_tag,
        "version": latest_tag.lstrip('v'),
        "version_code": latest_code,
        "update_available": update_available,
        "apk_download_url": f"https://github.com/{repo}/releases/download/{latest_tag}/DigiSmartDeck-{latest_tag}.apk",
        "raw_manifest_url": f"https://raw.githubusercontent.com/{repo}/main/version.json"
    }
    return manifest


def simulate_firebase_remote_config_check(client_ver):
    """
    Format manifest gratis via Firebase Remote Config / Firebase Hosting / Firestore:
    https://<project-id>.web.app/version.json
    """
    latest_ver = "1.21.2"
    client_parts, client_code = parse_semver(client_ver)
    latest_parts, latest_code = parse_semver(latest_ver)

    update_available = latest_code > client_code

    firebase_config = {
        "source": "Firebase Remote Config / Hosting",
        "parameters": {
            "latest_app_version": latest_ver,
            "min_required_version": "1.20.0",
            "apk_download_url": "https://digismartdeck.web.app/downloads/DigiSmartDeck.apk",
            "force_update": False
        },
        "evaluation": {
            "client_version": client_ver,
            "update_available": update_available,
            "action": "PROMPT_INSTALL" if update_available else "UP_TO_DATE"
        }
    }
    return firebase_config


def main():
    parser = argparse.ArgumentParser(description="Simulasi Auto-Updater DigiSmartDeck")
    parser.add_argument("--client-version", default="1.21.0", help="Versi yang terpasang di Tab/HP (misal 1.21.0)")
    parser.add_argument("--target-version", default="1.21.2", help="Versi target di server/cloud (misal 1.21.2)")
    args = parser.parse_args()

    print("=" * 65)
    print("  SIMULASI SISTEM AUTO-UPDATER DIGISMARTDECK")
    print("=" * 65)
    print(f"Perangkat Tablet / Klien : v{args.client_version}")
    print(f"Versi Server Terkini    : v{args.target_version}")
    print("-" * 65)

    # 1. Jalur Server Lokal (Aktif saat ini)
    local_res = simulate_local_server_check(args.client_version, args.target_version)
    print("[1] EVALUASI SERVER LOKAL PC (/api/updater/check):")
    print(f"    - Update Tersedia : {local_res['update_available']}")
    print(f"    - URL Unduhan     : {local_res['download_url']}")
    print(f"    - Nama Berkas APK : {local_res['apk_filename']} ({local_res['apk_size_mb']} MB)")
    if local_res['update_available']:
        print(f"    - Tindakan UI     : Tampilkan status 'Pasang Pembaruan Sekarang' & trigger download via DigiAndroidBridge")

    print("\n" + "-" * 65)

    # 2. Jalur GitHub Releases (Gratis 100%, bandwidth tanpa batas)
    gh_res = simulate_github_releases_check(args.client_version)
    print("[2] EVALUASI JALUR GRATIS GITHUB RELEASES:")
    print(f"    - Update Tersedia : {gh_res['update_available']}")
    print(f"    - Target Tag      : {gh_res['tag_name']}")
    print(f"    - URL APK         : {gh_res['apk_download_url']}")
    print(f"    - Manifest URL    : {gh_res['raw_manifest_url']}")

    print("\n" + "-" * 65)

    # 3. Jalur Firebase (Gratis Firebase Spark Plan)
    fb_res = simulate_firebase_remote_config_check(args.client_version)
    print("[3] EVALUASI JALUR GRATIS FIREBASE (Remote Config / Hosting):")
    print(f"    - Update Tersedia : {fb_res['evaluation']['update_available']}")
    print(f"    - Status Evaluasi : {fb_res['evaluation']['action']}")
    print(f"    - URL Unduhan     : {fb_res['parameters']['apk_download_url']}")
    print("=" * 65)


if __name__ == "__main__":
    main()
