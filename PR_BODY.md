## Summary
Tighten style guidance and optional lint checks to remove negative chaining and rhetorical opposites, and to avoid overly poetic structures.

### Changes
- **docs/canon/style_guide.md** — adds:
  - “Clarity over negation” with concrete before/after examples.
  - “Avoid rhetorical opposites” guidance.
  - “Keep figurative language restrained” guidance.
  - A **Chapter 09** trail example with the preferred rewrite.
- **docs/canon/prose_patterns.md** — quick “do / do not” sheet.
- **tools/lint_audio.py** — optional warnings:
  - `style-negation-chain`, `style-not-but`, `style-neither-nor`, `style-it-was-not`, `style-maxim-cadence`.

> Note: CI already lints only chapters. These new checks focus on single-sentence patterns to minimize noise.
