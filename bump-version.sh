#!/usr/bin/env bash
# ==============================================================================
# DigiKeyboard Semantic Versioning Automation Script (SemVer 2.0.0)
# ==============================================================================
# Penggunaan:
#   ./bump-version.sh patch   (1.4.1 -> 1.4.2 : Bugfix / perbaikan kecil)
#   ./bump-version.sh minor   (1.4.1 -> 1.5.0 : Fitur baru backward-compatible)
#   ./bump-version.sh major   (1.4.1 -> 2.0.0 : Perubahan besar / breaking change)
#   ./bump-version.sh 1.5.0   (Versi kustom spesifik)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION_FILE="VERSION"
CHANGELOG_FILE="CHANGELOG.md"

if [ ! -f "$VERSION_FILE" ]; then
    echo "1.4.1" > "$VERSION_FILE"
fi

CURRENT_VERSION=$(tr -d '[:space:]' < "$VERSION_FILE")

if [ -z "$CURRENT_VERSION" ]; then
    CURRENT_VERSION="1.4.1"
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
        # Jika argumen adalah nomor versi langsung, contoh: 1.5.0
        if [[ "$BUMP_TYPE" =~ ^[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
            NEW_VERSION="$BUMP_TYPE"
        else
            echo "❌ Tipe bump tidak valid: '$BUMP_TYPE'"
            echo "Penggunaan: ./bump-version.sh [patch|minor|major|<nomor-versi>] [deskripsi opsional]"
            exit 1
        fi
        ;;
esac

TODAY=$(date +"%Y-%m-%d")

echo "============================================================"
echo "  🚀 DigiKeyboard Automatic Version Bumper"
echo "============================================================"
echo "  Versi Saat Ini : v${CURRENT_VERSION}"
echo "  Versi Baru     : v${NEW_VERSION} ($BUMP_TYPE)"
echo "  Tanggal Rilis  : ${TODAY}"
echo "============================================================"

# 1. Update VERSION file
echo "$NEW_VERSION" > "$VERSION_FILE"
echo "[✓] File $VERSION_FILE berhasil diperbarui ke $NEW_VERSION"

# 2. Update CHANGELOG.md jika ada
if [ -f "$CHANGELOG_FILE" ]; then
    TMP_CHANGELOG=$(mktemp)
    DESC_TEXT="${CUSTOM_DESC:-Rilis versi $NEW_VERSION}"
    python3 -c "
import sys
content = open('$CHANGELOG_FILE', 'r', encoding='utf-8').read()
new_header = '## 🇮🇩 Bahasa Indonesia\n\n### [$NEW_VERSION] - $TODAY\n- $DESC_TEXT\n'
content = content.replace('## 🇮🇩 Bahasa Indonesia\n', new_header, 1)
new_en_header = '## 🇬🇧 English\n\n### [$NEW_VERSION] - $TODAY\n- Release v$NEW_VERSION updates\n'
content = content.replace('## 🇬🇧 English\n', new_en_header, 1)
open('$CHANGELOG_FILE', 'w', encoding='utf-8').write(content)
" 2>/dev/null || true
    echo "[✓] File $CHANGELOG_FILE berhasil diperbarui dengan entri v${NEW_VERSION}"
fi

# 3. Git Commit & Git Tag
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add "$VERSION_FILE" "$CHANGELOG_FILE" 2>/dev/null || git add "$VERSION_FILE"
    COMMIT_MSG="chore(release): bump version to v${NEW_VERSION}"
    if [ -n "$CUSTOM_DESC" ]; then
        COMMIT_MSG="chore(release): v${NEW_VERSION} - ${CUSTOM_DESC}"
    fi
    git commit -m "$COMMIT_MSG" || true
    
    # Hapus tag lokal jika sudah ada sebelumnya lalu buat tag baru
    git tag -d "v${NEW_VERSION}" 2>/dev/null || true
    git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}: ${CUSTOM_DESC:-Stable release checkpoint}"
    echo "[✓] Git commit & Git tag 'v${NEW_VERSION}' berhasil dibuat"
fi

# 4. Restart service (systemd atau PM2)
if systemctl is-active digikeyboard.service >/dev/null 2>&1; then
    pkill -f "python3.*/server.py" 2>/dev/null || true
    echo "[✓] Layanan systemd digikeyboard berhasil disegarkan"
elif command -v pm2 >/dev/null 2>&1; then
    if pm2 describe digikeyboard >/dev/null 2>&1; then
        pm2 restart digikeyboard >/dev/null 2>&1 || true
        echo "[✓] Layanan PM2 digikeyboard berhasil direstart"
    fi
fi

echo "============================================================"
echo "✅ Sukses! Versi sekarang adalah v${NEW_VERSION}"
echo "Untuk mengunggah commit dan tag ke GitHub, jalankan:"
echo "  git push origin main --tags"
echo "============================================================"
