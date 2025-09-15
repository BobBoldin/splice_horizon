#!/usr/bin/env python3
import re, sys, pathlib

# --- Patterns ---
APO = r"[\'’]"

# Contractions (allow possessive 's like "Elias’s")
ALWAYS_CONTRACTIONS = re.compile(
    rf"\b\w+{APO}(?:n[tT]|re|ve|ll|d|m)\b"
)
_S_WORDS = ("it","that","there","here","where","who","what","how","when","why",
            "he","she","we","they","you","let")
S_CONTRACTIONS = re.compile(
    rf"\b(?:{'|'.join(_S_WORDS)}){APO}[sS]\b"
)

EM_DASH_RE = re.compile("\u2014")
DIGIT_RE = re.compile(r"\d")
SYMBOL_RE = re.compile(r"[#$%&@]")

# Chapter title line matcher (e.g., "# Chapter 01 - Title" or "Chapter 08 — Title")
TITLE_RE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:Chapter|CHAPTER)\s+\d+\b")

def lint(text: str):
    warnings = []

    # Find first non-empty line index (1-based)
    lines = text.splitlines()
    title_idx = None
    for idx, ln in enumerate(lines, 1):
        if ln.strip():
            title_idx = idx
            break

    for i, line in enumerate(lines, 1):
        # Contractions
        if ALWAYS_CONTRACTIONS.search(line) or S_CONTRACTIONS.search(line):
            warnings.append((i, "contraction", line.rstrip()))

        # Em dash
        if EM_DASH_RE.search(line):
            warnings.append((i, "em-dash", line.rstrip()))

        # Digits (spell numbers) — but skip if this is the chapter title line
        if not (title_idx == i and TITLE_RE.search(line)):
            if DIGIT_RE.search(line):
                warnings.append((i, "digit", line.rstrip()))

        # Symbols to spell out (tune as needed)
        if SYMBOL_RE.search(line):
            warnings.append((i, "symbol", line.rstrip()))

    return warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/lint_audio.py <file1> [file2...]", file=sys.stderr)
        sys.exit(1)
    exit_code = 0
    for path in sys.argv[1:]:
        p = pathlib.Path(path)
        if not p.exists():
            print(f"[error] Not found: {p}", file=sys.stderr)
            exit_code = 2
            continue
        text = p.read_text(encoding="utf-8")
        warns = lint(text)
        if warns:
            print(f"== {p} ==")
            for ln, kind, snippet in warns:
                print(f"  L{ln:>4}  {kind:11}  {snippet}")
            exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
