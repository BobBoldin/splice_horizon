#!/usr/bin/env python3
import re, sys, pathlib

CONTRACTION_RE = re.compile(r"\b\w+'(t|re|ve|m|ll|d|s)\b")
DIGIT_RE = re.compile(r"\d")
EM_DASH_RE = re.compile("\u2014")
SYMBOL_RE = re.compile(r"[#$%&@]")

def lint(text):
    warnings = []
    for i, line in enumerate(text.splitlines(), 1):
        if CONTRACTION_RE.search(line):
            warnings.append((i, "contraction", line.strip()))
        if EM_DASH_RE.search(line):
            warnings.append((i, "em-dash", line.strip()))
        if DIGIT_RE.search(line):
            warnings.append((i, "digit", line.strip()))
        if SYMBOL_RE.search(line):
            warnings.append((i, "symbol", line.strip()))
    return warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/lint_audio.py <file1> [file2...]")
        sys.exit(1)
    exit_code = 0
    for path in sys.argv[1:]:
        p = pathlib.Path(path)
        if not p.exists():
            print(f"[error] Not found: {p}")
            exit_code = 2
            continue
        text = p.read_text(encoding="utf-8")
        warns = lint(text)
        if warns:
            print(f"== {p} ==")
            for ln, kind, snippet in warns:
                print(f"  L{ln:>4}  {kind:10}  {snippet}")
            exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
