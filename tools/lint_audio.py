#!/usr/bin/env python3
import re, sys, pathlib

# Apostrophes (straight or curly)
APO = r"[\'’]"

# True contractions (leave possessives alone)
ALWAYS_CONTRACTIONS = re.compile(rf"\b\w+{APO}(?:n[tT]|re|ve|ll|d|m)\b")
_S_WORDS = ("it","that","there","here","where","who","what","how","when","why",
            "he","she","we","they","you","let")
S_CONTRACTIONS = re.compile(rf"\b(?:{'|'.join(_S_WORDS)}){APO}[sS]\b")

# Em dashes, digits, and symbols
EM_DASH_RE = re.compile("\u2014")
DIGIT_RE = re.compile(r"\d")
SYMBOL_RE = re.compile(r"[#$%&@]")

# Title line pattern (skip digit warnings there)
TITLE_RE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:Chapter|CHAPTER)\s+\d+\b")

# Style checks (single-sentence scope)
NEG_CHAIN = re.compile(r"\bnot\s+\w+(?:\s*,\s*not\s+\w+)+(?:\s*,\s*but\s+\w+)?", re.I)
NOT_BUT = re.compile(r"\bnot\b[^.?!]{0,200}\bbut\b", re.I)
NEITHER_NOR = re.compile(r"\bneither\b[^.?!]{0,200}\bnor\b", re.I)
IT_WAS_NOT = re.compile(r"\bit was not\b", re.I)
MAXIM_CADENCE = re.compile(r"\bIf\b[^.]{0,80}\bI will\b[^.]*\.\s*\bIf\b[^.]{0,80}\bI will\b", re.I)

def lint(text: str):
    warnings = []
    lines = text.splitlines()

    # First non-empty line for title detection
    title_idx = next((i for i,l in enumerate(lines,1) if l.strip()), None)

    for i, line in enumerate(lines, 1):
        # Contractions
        if ALWAYS_CONTRACTIONS.search(line) or S_CONTRACTIONS.search(line):
            warnings.append((i, "contraction", line.rstrip()))

        # Em dash
        if EM_DASH_RE.search(line):
            warnings.append((i, "em-dash", line.rstrip()))

        # Digits (skip chapter title)
        if not (title_idx == i and TITLE_RE.search(line)):
            if DIGIT_RE.search(line):
                warnings.append((i, "digit", line.rstrip()))

        # Symbols to spell
        if SYMBOL_RE.search(line):
            warnings.append((i, "symbol", line.rstrip()))

        # Style: negation / opposites / maxims
        if NEG_CHAIN.search(line):
            warnings.append((i, "style-negation-chain", line.rstrip()))
        else:
            if NOT_BUT.search(line):
                warnings.append((i, "style-not-but", line.rstrip()))
            if NEITHER_NOR.search(line):
                warnings.append((i, "style-neither-nor", line.rstrip()))
            if IT_WAS_NOT.search(line):
                warnings.append((i, "style-it-was-not", line.rstrip()))
            if MAXIM_CADENCE.search(line):
                warnings.append((i, "style-maxim-cadence", line.rstrip()))

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
                print(f"  L{ln:>4}  {kind:21}  {snippet}")
            exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
