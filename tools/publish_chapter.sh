#!/usr/bin/env bash
set -euo pipefail
SRC="C:\\Users\\bobbo\\OneDrive\\Documents\\bob\\Splice_Horizon\\chapters"

tools/convert_docx_to_md.sh "$SRC"
python tools/update_mkdocs_nav.py --apply || true
python tools/lint_audio.py docs/episodes/ch??/draft.md || true

git add -A
msg="update: chapters + canon sync"
[ $# -gt 0 ] && msg="$*"
git commit -m "$msg" || echo "No changes to commit."
git push origin main
echo "[done] pushed to main."

