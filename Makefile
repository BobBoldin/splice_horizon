# Makefile — Splice Horizon

.PHONY: lint lint-all serve build-docs

# Lint chapter drafts only
lint:
	python tools/lint_audio.py $(shell git ls-files 'docs/episodes/ch??/draft.md')

# (Optional) Lint every Markdown file in the repo
lint-all:
	python tools/lint_audio.py $(shell git ls-files '*.md')

# Serve the canon site locally (requires mkdocs & mkdocs-material)
serve:
	mkdocs serve

# Build static site to ./site
build-docs:
	mkdocs build

