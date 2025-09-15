#!/usr/bin/env bash
# tools/convert_docx_to_md.sh
# Convert .docx chapters to Markdown under docs/episodes/chXX/draft.md using pandoc.
# Works in Git Bash on Windows (handles C:\ paths) and on macOS/Linux.

set -euo pipefail

need() { command -v "$1" >/dev/null 2>&1 || { echo "[error] $1 is not installed"; exit 1; }; }
need pandoc
command -v git >/dev/null 2>&1 || true

if [ $# -lt 1 ]; then
  echo "Usage: tools/convert_docx_to_md.sh \"<path-to-docx-folder>\"" >&2
  echo "Example: tools/convert_docx_to_md.sh \"C:\\Users\\bobbo\\OneDrive\\Documents\\bob\\Splice_Horizon\\chapters\"" >&2
  exit 1
fi

SRC_INPUT="$1"

# Normalize the source path (Git Bash + Windows safe)
if command -v cygpath >/dev/null 2>&1; then
  SRC_DIR="$(cygpath -u "$SRC_INPUT" 2>/dev/null || echo "$SRC_INPUT")"
else
  SRC_DIR="$SRC_INPUT"
fi

if [ ! -d "$SRC_DIR" ]; then
  echo "[error] Source directory not found: $SRC_DIR" >&2
  exit 2
fi

# Repo root (ok if git is not present)
ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
OUT_ROOT="$ROOT_DIR/docs/episodes"
mkdir -p "$OUT_ROOT"

# Guard: no matches
if ! compgen -G "$SRC_DIR"/*.docx >/dev/null; then
  echo "[done] No .docx files in: $SRC_DIR"
  exit 0
fi

converted=()

for f in "$SRC_DIR"/*.docx; do
  base="$(basename "$f")"

  # Extract chapter number from filename (no [[ =~ ]], just sed)
  num="$(printf "%s" "$base" | sed -n 's/.*[Cc][Hh]\(apter\)\{0,1\}[ _-]*\([0-9][0-9]*\).*/\2/p')"
  if [ -z "${num}" ]; then
    # fallback: first 1–2 digit group
    num="$(printf "%s" "$base" | sed -n 's/.*\([0-9][0-9]\).*/\1/p')"
  fi
  if [ -z "${num}" ]; then
    num="$(printf "%s" "$base" | sed -n 's/.*\([0-9]\).*/\1/p')"
  fi

  if [ -z "$num" ]; then
    echo "[warn] Could not detect chapter number from '$base'; skipping."
    continue
  fi

  # Zero-pad to 2 digits
  num=$((10#$num))
  printf -v num2 "%02d" "$num"
  out_dir="$OUT_ROOT/ch${num2}"
  mkdir -p "$out_dir"
  out_md="$out_dir/draft.md"

  echo "[info] Converting: $base -> docs/episodes/ch${num2}/draft.md"
  pandoc "$f" -o "$out_md" --wrap=none

  # Add a small README with checklist if not present
  if [ ! -f "$out_dir/README.md" ]; then
    cat > "$out_dir/README.md" <<EOF
# Chapter ${num} Checklist

- Target length: around two thousand five hundred words (plus or minus three hundred)
- No contractions, numbers spelled, no em dashes
- Dialogue conversational; narration carries senses
- Spoken transitions at scene shifts
EOF
  fi

  converted+=("$out_md")
done

echo ""
if [ ${#converted[@]} -eq 0 ]; then
  echo "[done] No chapters converted."
  exit 0
fi

# Optional: run the audio linter if present
if [ -f "$ROOT_DIR/tools/lint_audio.py" ]; then
  echo "[info] Running audio linter on converted files..."
  python "$ROOT_DIR/tools/lint_audio.py" "${converted[@]}" || true
else
  echo "[hint] Linter not found at tools/lint_audio.py; skip."
fi

echo "[done] Converted ${#converted[@]} chapter(s)."
