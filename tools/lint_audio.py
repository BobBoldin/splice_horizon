#!/usr/bin/env python3
"""
Lightweight Markdown linter for Splice Horizon style rules.

What it enforces:
- Em dashes (—) are banned. Use colon or period instead.
- Soft/discretionary hyphens (U+00AD) are banned.
- Line-breaking hyphens (a visible '-' at the end of a line) are banned.
- Numbers: spell out in narration. Digits are OK in dialogue, code/logs, units, and IDs.
- Contractions are allowed.

Scans files under: docs/, episodes/
Targets extensions: .md, .mdx

Exit code:
- 0 when no issues found
- 1 when any issues are found
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

# Where to scan
PATHS: tuple[str, ...] = ("episodes")
EXTS: set[str] = {".md", ".mdx"}

# --- Regex rules ---

# Always banned
EM_DASH = re.compile(r"—")              # U+2014
SOFT_HYPHEN = re.compile("\u00AD")      # U+00AD (SHY)

# Hyphen used for line breaking (visible ASCII '-' at end of line)
LINE_BREAKING_HYPHEN = re.compile(r"-\s*$")

# Digits (we scope this to narration only)
DIGIT = re.compile(r"\b\d+\b")

# Code fence (```)
CODE_FENCE = re.compile(r"^```")

# YAML front matter fence (--- on its own line)
MD_FRONT_MATTER = re.compile(r"^---\s*$")

# Dialogue heuristic: treat as dialogue if the line begins with a quote mark (ASCII or curly)
DIALOGUE_STARTS = ('"', "“", "‘", "'")

# Units and percent patterns where digits are allowed even in narration
UNITS_OK = re.compile(
    r"\b("
    r"°C|°F|mm|cm|m|km|mg|g|kg|mL|L|ml|l|fps|MHz|GHz|kHz|Hz|%"
    r")\b"
)

# IDs / labels commonly used in your docs where digits are fine
ID_OK = re.compile(
    r"\b("
    r"Deck\s?\d+|Bay\s?\d+|Ring\s?\d+|Section\s?\d+|Kestrel-\d+|VR-?\d+|ID:\s?\d+"
    r")\b",
    re.IGNORECASE,
)

def iter_files(paths: Iterable[str] = PATHS, exts: Iterable[str] = EXTS) -> Iterable[Path]:
    for base in paths:
        pbase = Path(base)
        if not pbase.exists():
            continue
        for p in pbase.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                yield p

def is_dialogue(line: str) -> bool:
    s = line.lstrip()
    return s.startswith(DIALOGUE_STARTS)

def lint_text(lines: List[str], path: Path) -> List[Tuple[int, str]]:
    errors: List[Tuple[int, str]] = []
    in_code = False
    in_front_matter = False

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # Toggle code fences
        if CODE_FENCE.match(line):
            in_code = not in_code

        # Toggle front matter fences
        if MD_FRONT_MATTER.match(line) and i == 1:
            # Only treat the very first '---' as starting front matter
            in_front_matter = True
        elif MD_FRONT_MATTER.match(line) and in_front_matter:
            # Closing front matter
            in_front_matter = False

        # Always ban em dashes
        if EM_DASH.search(line):
            errors.append((i, "Use a colon or period instead of an em dash (—)."))

        # Soft hyphens are forbidden anywhere
        if SOFT_HYPHEN.search(line):
            errors.append((i, "Remove soft hyphen (U+00AD). Do not insert hidden hyphens."))

        # Line-breaking hyphen (visible '-' at end of line)
        if LINE_BREAKING_HYPHEN.search(line):
            errors.append((i, "Do not break a word across lines with a trailing hyphen. Keep hyphenated words on one line."))

        # Number rule: only enforce in narration (not in code, front matter, or dialogue)
        if not in_code and not in_front_matter and not is_dialogue(line):
            if DIGIT.search(line):
                # Allow digits when paired with known units/IDs
                if UNITS_OK.search(line) or ID_OK.search(line):
                    pass
                else:
                    errors.append((i, "Spell out numbers in narration. Digits are fine in dialogue, code/logs, units, and IDs."))

    return errors

def main() -> int:
    any_errors = False
    for p in iter_files():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback if weird encoding slips in
            text = p.read_text(encoding="utf-8", errors="replace")

        lines = text.splitlines()
        issues = lint_text(lines, p)
        if issues:
            any_errors = True
            for ln, msg in issues:
                print(f"{p}:{ln}: {msg}")

    return 1 if any_errors else 0

if __name__ == "__main__":
    sys.exit(main())
