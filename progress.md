<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: M0 session (bootstrap, feasibility, M1 drafts)

**Milestone:** M0, plus M1 drafts. **Next bounded task at start:** create control files and the protocol proposal.

### Starting state
`git status`: branch main, "nothing to commit, working tree clean". One commit (3614dbe): master prompt and the owner's licence package.

### Commands and actual outputs
- `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize`: `Apple M1 Pro`, `10`, `17179869184`.
- `sw_vers`: macOS 15.3.1, build 24D70.
- `df -h /Users/bechir`: 460Gi size, 311Gi used, 129Gi available.
- `/usr/local/bin/python3 --version`: Python 3.12.1.
- `.tools/py/bin/uv --version`: uv 0.9.5 (d5f39331a 2025-10-21).
- `.tools/py/bin/typst --version`: no such file. typst exists only as a Python package: version 0.15.0 (pypdf 6.20.0, pillow 11.3.0).
- `.tools/pandoc --version`: pandoc 3.6.3.
- `helix/.tools/node/bin/node --version`: v22.23.3 (read-only use).
- `git --version`: 2.42.1. `which tex pdflatex xelatex`: not found.
- `uv lock`: "Resolved 8 packages in 5ms", exit 0. Locked numpy 2.3.5, pytest 8.4.2.
- `uv sync`: installed iniconfig 2.3.1, numpy 2.3.5, packaging 26.3, pluggy 1.7.0, pygments 2.21.0, pytest 8.4.2; exit 0.
- `uv run pytest -q` (exploratory toolchain smoke, no research code): "2 passed in 1.58s".
- PDF toolchain smoke (exploratory, outputs in the session scratchpad, not committed): `pandoc research/paper/manuscript.md -s -t typst` then `typst.compile(...)` failed with `typst.TypstError: font fallback list must not be empty`. Retried with `-V mainfont="Libertinus Serif"`: 1-page PDF, text extracted with pypdf starts "Manuscript skeleton (headings only...". `pandoc -t latex -s` produced a .tex file, exit 0 (not compiled; no TeX).

### Web sources
WebSearch and WebFetch on 2026-11-24. Opened: arXiv abstract pages 1710.11214, 1902.10730, 1909.04847, 2107.08959, 1003.0146, 2007.13019; OpenAlex record for doi:10.1145/3240323.3240372; Kalimeris et al. author PDF (first page); Carbonell and Goldstein author PDF (first page); GroupLens ml-latest-small README (licence); kuairec.com (licence). An arXiv id guessed for one paper (1909.13093) turned out to be an unrelated astrophysics paper and was discarded. dblp and one webis page were not reachable (bot protection, HTTP 404). MIND licence known only from search summaries (unverified). No dataset downloaded.

### Decisions
D-001 (owner licence), D-002 (toolchain), D-003 (synthetic only, proposal), D-004 (protocol v0.1 draft), D-005 (dependency cutoff). See `research/decision_log.md`.

### Files created
CLAUDE.md, roadmap.md, progress.md, README.md, CITATION.cff, pyproject.toml, uv.lock, src/pulse/__init__.py, tests/test_toolchain_smoke.py, data/manifest.json, results/README.md, experiments/README.md, demo/README.md, articles/README.md, research/{protocol.md, decision_log.md, literature_review.md, limitations.md, claims_register.csv, experiment_journal.jsonl, experiment_registry.csv}, research/experiments/EXP-00{1,2,3}/protocol.md, research/paper/{manuscript.md, supplementary.md, references.bib, figures/README.md}, research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}. CONTRIBUTING.md: development commands appended (section 6). Licence files unchanged.

### Not done (by design or blocked)
- No confirmatory or exploratory research run: no simulation code exists yet (M2).
- No protocol frozen (G-FREEZE: owner).
- `manuscript.tex`, PDFs, experiment reports, run manifests, metrics files: not created, because no content or results exist; creating them now would be placeholders.
- `research/experiment_journal.jsonl` is empty: no experiment has run (toolchain smoke is recorded here instead, as it tests no hypothesis).

### Outstanding risks
- The primary contrast is expected by construction; the value lies in effect sizes and the sensitivity analysis (stated in the protocol).
- Steck 2018 miscalibration formula not yet checked against full text.
- Seed count may need to rise to 20 after the smoke run.
- Demo needs npm dependencies at M5; Node is borrowed read-only.

### Next action
Owner: review protocol draft and decisions D-003, D-004. Session: implement the M2 core (random baseline first), then run the exploratory smoke matrix to settle the seed count before the owner freezes.
