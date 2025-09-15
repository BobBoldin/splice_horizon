#!/usr/bin/env python3
# tools/update_mkdocs_nav.py

"""
Regenerate the "Episodes" nav block in mkdocs.yml by scanning docs/episodes/chXX folders.

Usage:
  python tools/update_mkdocs_nav.py --print        # print the episodes nav block
  python tools/update_mkdocs_nav.py --apply        # replace between markers in mkdocs.yml

Add these markers to mkdocs.yml once:
  # BEGIN AUTO-EPISODES
  # END AUTO-EPISODES
"""

import os, sys, re, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
EP_DIR = ROOT / "docs" / "episodes"
MKDOCS = ROOT / "mkdocs.yml"

def list_episodes():
    eps = []
    if EP_DIR.exists():
        for d in sorted(EP_DIR.iterdir()):
            if d.is_dir() and re.match(r"ch\d{2}$", d.name):
                num = d.name[2:]
                title = f"Chapter {int(num)}"
                path = f"episodes/{d.name}/draft.md"
                eps.append((title, path))
    return eps

def render_nav_block(eps):
    lines = ["  - Episodes:"]
    for title, path in eps:
        lines.append(f"      - {title}: {path}")
    return "\n".join(lines) + "\n"

def print_block():
    eps = list_episodes()
    sys.stdout.write(render_nav_block(eps))

def apply_block():
    if not MKDOCS.exists():
        sys.stderr.write("[error] mkdocs.yml not found.\n")
        sys.exit(1)
    text = MKDOCS.read_text(encoding="utf-8")
    m_start = re.search(r"^[^\S\r\n]*# BEGIN AUTO-EPISODES.*$", text, re.M)
    m_end = re.search(r"^[^\S\r\n]*# END AUTO-EPISODES.*$", text, re.M)
    block = render_nav_block(list_episodes())
    if m_start and m_end and m_start.end() <= m_end.start():
        new = text[:m_start.end()] + "\n" + block + text[m_end.start():]
    else:
        sys.stderr.write("[error] Markers not found or malformed. Add them to mkdocs.yml and re-run.\n")
        sys.exit(2)
    MKDOCS.write_text(new, encoding="utf-8")
    print("[done] mkdocs.yml Episodes nav updated.")

if __name__ == "__main__":
    if "--print" in sys.argv:
        print_block()
    elif "--apply" in sys.argv:
        apply_block()
    else:
        print(__doc__)
