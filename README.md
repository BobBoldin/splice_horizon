# Orivay / Splice Horizon — Story Dev as Code Kit (v1)

This kit gives you a repo-style workflow for the series:
- **Docs-as-code** with Markdown + MkDocs (optional).
- **Canon folders** for characters, world, rules, weapons.
- **Episodes** in their own folders with a template.
- **Lint** script to enforce audio rules (no contractions, numbers spelled, no em dashes).
- **Git-ready**: commit, branch per chapter, pull request review, changelog.

## Suggested Git Workflow
1. Create a repo (GitHub/GitLab/Bitbucket).
2. Push this kit as the initial commit.
3. For a new chapter, create a branch: `feat/ch08-first-landing`.
4. Draft in `episodes/ch08/`.
5. Run `python tools/lint_audio.py episodes/ch08/draft.md` and fix warnings.
6. Open a PR; use `docs/canon/changelog.md` to note canon changes.
7. Merge when happy; tag a version like `v0.8.0`.

## Build the docs site (optional)
- Install MkDocs: `pip install mkdocs`
- Serve: `mkdocs serve` (opens http://127.0.0.1:8000)
- Build: `mkdocs build` (outputs to `site/`)

