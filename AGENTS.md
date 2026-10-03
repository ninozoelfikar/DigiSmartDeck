# AGENT INSTRUCTIONS FOR DIGISMARTDECK

Whenever you start a session in this repository, you MUST read `PROJECT_CONTEXT.md` first.

## Core Rules:
1. STRICT ZERO EMOJIS / ZERO EMOTICONS across all code, logs, UI, and assistant text.
2. Preserve mechanical click sound (`playClickSound()`) on interactive keyboard and workstation buttons.
3. Mobile client must stay lightweight (~20 MB Android APK). Do not bundle AI models in the mobile client.
4. Active working branch: `test/concept-a-deck`.
5. Background service: `digikeyboard.service` (restart via `pkill -f "/home/nino/digikeyboard/server.py"`).
6. Respon pasca-tugas: Cukup jawab 'Selesai' atau 'Done' setelah tugas selesai, KECUALI jika pengguna secara eksplisit meminta penjelasan.
