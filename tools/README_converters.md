# Conversion Tools

## Git Bash (bash) — recommended
```
tools/convert_docx_to_md.sh "C:\Users\bobbo\OneDrive\Documents\bob\Splice_Horizon\chapters"
```

## PowerShell
```
pwsh -File tools/Convert-DocxToMd.ps1 -Source "C:\Users\bobbo\OneDrive\Documents\bob\Splice_Horizon\chapters"
```

### After converting
- Commit the new `docs/episodes/chXX/draft.md` files.
- Optional: update MkDocs nav automatically.

#### Auto-update MkDocs nav (optional)
1) Add these markers to your `mkdocs.yml` once under the nav section:
```
  # BEGIN AUTO-EPISODES
  # END AUTO-EPISODES
```
2) Then run:
```
python tools/update_mkdocs_nav.py --apply
```
or print the block to paste:
```
python tools/update_mkdocs_nav.py --print
```
