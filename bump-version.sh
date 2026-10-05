#!/usr/bin/env bash
# ==============================================================================
# DigiSmartDeck Semantic Versioning Automation Script (SemVer 2.0.0)
# ==============================================================================
# Penggunaan:
#   ./bump-version.sh patch   (1.17.0 -> 1.17.1 : Bugfix / perbaikan kecil)
#   ./bump-version.sh minor   (1.17.0 -> 1.18.0 : Fitur baru backward-compatible)
#   ./bump-version.sh major   (1.17.0 -> 2.0.0  : Perubahan besar / breaking change)
#   ./bump-version.sh 1.18.0  (Versi kustom spesifik)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION_FILE="VERSION"
CHANGELOG_FILE="CHANGELOG.md"

if [ ! -f "$VERSION_FILE" ]; then
    echo "1.17.0" > "$VERSION_FILE"
fi

CURRENT_VERSION=$(tr -d '[:space:]' < "$VERSION_FILE")

if [ -z "$CURRENT_VERSION" ]; then
    CURRENT_VERSION="1.17.0"
fi

# Parsing semver: MAJOR.MINOR.PATCH
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
MAJOR=${MAJOR:-1}
MINOR=${MINOR:-0}
PATCH=${PATCH:-0}

BUMP_TYPE="${1:-patch}"
CUSTOM_DESC="${2:-}"

case "$BUMP_TYPE" in
    patch|p)
        PATCH=$((PATCH + 1))
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
        ;;
    minor|m)
        MINOR=$((MINOR + 1))
        PATCH=0
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
        ;;
    major|M)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
        ;;
    *)
        if [[ "$BUMP_TYPE" =~ ^[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
            NEW_VERSION="$BUMP_TYPE"
            IFS='.' read -r MAJOR MINOR PATCH <<< "$NEW_VERSION"
        else
            echo "[ERROR] Tipe bump tidak valid: '$BUMP_TYPE'"
            echo "Penggunaan: ./bump-version.sh [patch|minor|major|<nomor-versi>] [deskripsi opsional]"
            exit 1
        fi
        ;;
esac

TODAY=$(date +"%Y-%m-%d")

echo "============================================================"
echo "  DigiSmartDeck Automatic Version Bumper"
echo "============================================================"
echo "  Versi Saat Ini : v${CURRENT_VERSION}"
echo "  Versi Baru     : v${NEW_VERSION} ($BUMP_TYPE)"
echo "  Tanggal Rilis  : ${TODAY}"
echo "============================================================"

# 1. Update VERSION file
echo "$NEW_VERSION" > "$VERSION_FILE"
echo "[OK] File $VERSION_FILE berhasil diperbarui ke $NEW_VERSION"

# 2. Update CHANGELOG.md jika ada
if [ -f "$CHANGELOG_FILE" ]; then
    DESC_TEXT="${CUSTOM_DESC:-Rilis versi $NEW_VERSION}"
    python3 -c "
import sys
content = open('$CHANGELOG_FILE', 'r', encoding='utf-8').read()
new_header = '## Bahasa Indonesia\n\n### [$NEW_VERSION] - $TODAY\n- $DESC_TEXT\n'
content = content.replace('## Bahasa Indonesia\n', new_header, 1)
content = content.replace('## 🇮🇩 Bahasa Indonesia\n', new_header, 1)
new_en_header = '## English\n\n### [$NEW_VERSION] - $TODAY\n- Release v$NEW_VERSION updates\n'
content = content.replace('## English\n', new_en_header, 1)
content = content.replace('## 🇬🇧 English\n', new_en_header, 1)
open('$CHANGELOG_FILE', 'w', encoding='utf-8').write(content)
" 2>/dev/null || true
    echo "[OK] File $CHANGELOG_FILE berhasil diperbarui dengan entri v${NEW_VERSION}"
fi

# 3. Sinkronkan placeholder statis di UI
python3 -c "
import re

# Update static/index.html fallback version badge
try:
    with open('static/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    html = re.sub(r'DigiSmartDeck v[0-9.]+', 'DigiSmartDeck v$NEW_VERSION', html)
    html = re.sub(r'<span id=\"about-app-version\"([^>]*)>v[0-9.]+<', r'<span id=\"about-app-version\"\1>v$NEW_VERSION<', html)
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('[OK] static/index.html tersinkronisasi ke v$NEW_VERSION')
except Exception as e:
    print('[WARN] Gagal menyinkronkan static/index.html:', e)

# Update landing page badge
for landing_path in ['static/landing.html', 'landing/index.html']:
    try:
        with open(landing_path, 'r', encoding='utf-8') as f:
            l_html = f.read()
        l_html = re.sub(r'PRO V[0-9.]+', 'PRO V${MAJOR}.${MINOR}', l_html)
        with open(landing_path, 'w', encoding='utf-8') as f:
            f.write(l_html)
        print(f'[OK] {landing_path} tersinkronisasi ke PRO V${MAJOR}.${MINOR}')
    except Exception as e:
        pass
"

# 4. Kompilasi ulang APK Android jika environment Android tersedia
if [ -f "./build-apk.sh" ]; then
    echo "[OK] Mengompilasi ulang APK Android dengan versi baru..."
    ./build-apk.sh || echo "[WARN] Kompilasi APK dilewati atau gagal"
fi

# 5. Git Commit & Git Tag
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add "$VERSION_FILE" "$CHANGELOG_FILE" "PROJECT_CONTEXT.md" "auth_manager.py" "android/app/build.gradle" "android/app/src/main" "server.py" "static/index.html" "static/landing.html" "landing/index.html" dist/*.apk static/*.apk 2>/dev/null || git add "$VERSION_FILE"
    COMMIT_MSG="chore(release): bump version to v${NEW_VERSION}"
    if [ -n "$CUSTOM_DESC" ]; then
        COMMIT_MSG="chore(release): v${NEW_VERSION} - ${CUSTOM_DESC}"
    fi
    git commit -m "$COMMIT_MSG" || true
    
    # Hapus tag lokal jika sudah ada sebelumnya lalu buat tag baru
    git tag -d "v${NEW_VERSION}" 2>/dev/null || true
    git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}: ${CUSTOM_DESC:-Stable release checkpoint}"
    echo "[OK] Git commit dan Git tag 'v${NEW_VERSION}' berhasil dibuat"
fi

# 6. Restart server PC
pkill -f "/home/nino/digikeyboard/server.py" 2>/dev/null || true
echo "[OK] Layanan server PC disegarkan"

echo "============================================================"
echo "[OK] Sukses! Versi aplikasi sekarang adalah v${NEW_VERSION}"
echo "============================================================"
