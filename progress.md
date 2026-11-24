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

## 2026-11-24: M2 session (core implementation, exploratory smoke runs)

**Milestone:** M2 (protocol still DRAFT v0.1; no freeze, no confirmatory run). **Next bounded task at start:** implement the random baseline and the four rankers with schema, manifests, runner, report generator and CLI; then run the exploratory smoke matrix.

### Starting state
`git status`: branch main, clean, HEAD 36c143c.

### Implemented (commit b904855, plus records commit)
- `src/pulse/`: `config.py` (validated, hashable SimConfig), `model.py` (synthetic catalog, Dirichlet users, pools, choice, drift; SeedSequence streams per component, common random numbers across arms), `rankers.py` (random baseline, popularity, content similarity, LinUCB with Sherman-Morrison, MMR; one seeded tie rule), `simulate.py` (loop with built-in invariant checks), `metrics.py`, `stats.py` (paired t, bootstrap, d_z, Holm; t quantiles from the incomplete beta function, no scipy), `schema.py` (result schema 1.0.0, validated at export and import), `manifest.py` (config hash, seed, git revision and dirty flag, Python, numpy, OS, CPU, runtime, process peak RSS), `runner.py` (matrix expansion, failure recording, refusal of confirmatory configs unless the registry hash matches a frozen protocol, refusal to overwrite results), `report.py` (CSV, SVG, Markdown, pandoc to Typst PDF with `-V mainfont="Libertinus Serif"`), `cli.py` (`smoke`, `run`, `report`, `test`).
- `experiments/EXP-00{1,2,3}.json` (confirmatory, 240/240/120 runs, refused while unfrozen) and `experiments/exploratory/*.json`.
- Tests: `tests/test_config_metrics_stats.py`, `test_model_rankers.py`, `test_simulate.py`, `test_schema_runner_report.py` cover invalid inputs, golden values (entropy, Gini, KL, t quantiles, paired summary, Holm, drift, MMR hand example), properties (Gini bounds and invariances, simplex preservation), differential checks (Gini against O(N^2) definition, LinUCB against direct inverse, MMR with lambda 1 against similarity, H_exp against a naive loop), and the section 10 checks: ranking ties, feedback updates, seed determinism, topic distributions, zero-feedback behaviour.

### Commands and actual outputs
- First test run: `uv run pytest -q`: "5 failed, 104 passed". Causes: a test passed `None` where LinUCB read the slate shape (code fixed to use the embedding shape); two test thresholds were wrong (primary-topic argmax share is 0.944, not above 0.95; random-topic drift does not concentrate); and one real defect: LinUCB cold-start ties were decided by round-off (D-006, fixed by rounding scores to 12 decimals).
- After fixes: `uv run pytest -q`: "110 passed in 1.63s". Final run before the records commit: "110 passed in 5.65s".
- `uv lock`: "Updated pulse-feed-ranking v0.0.0 -> v0.1.0" (no dependency added; numpy 2.3.5, pytest 8.4.2).
- `PYTHONPATH=src uv run python -m pulse.cli run --experiment EXP-001`: "REFUSED: refusing confirmatory run of EXP-001: research/protocol.md is marked DRAFT" (exit code 3, also asserted in tests).
- Exploratory sets, all at clean revision b904855, every run status ok (0 failed), seeds disjoint from confirmatory seeds (`/usr/bin/time -l` wall clock including interpreter start):

| Set | Runs | Set wall clock (s) | Max RSS (bytes) |
| --- | --- | --- | --- |
| smoke (U 50, N 300, T 60, 2 seeds) | 10 | 0.51 | 46399488 |
| var-probe (EXP-001 primary cell, full size, 10 seeds) | 50 | 56.30 | 144457728 |
| sweep-EXP-001 (all 24 cells, 2 seeds) | 48 | 57.34 | 146276352 |
| sweep-EXP-002 (all 24 cells, 2 seeds) | 48 | 61.43 | 140492800 |
| sweep-EXP-003 (all 12 cells, 2 seeds) | 24 | 74.78 | 132775936 |

  sweep-EXP-003 used 25.2 s user CPU for 75.0 s real, so the machine was probably busy with other work during that set; its per-run times (mean 2.4 to 4.4 s by arm) are pessimistic.
- Reports: `pulse.cli report --results results/exploratory/<set>` for all five sets; PDFs built (2, 2, 4, 4, 2 pages), text extracted with pypdf, two pages inspected as rendered images.

### Exploratory measurements (planning values only, not findings)
- Runtime per full-size run (var-probe means by arm): random 0.76 s, popularity 0.73 s, similarity 0.78 s, LinUCB 1.18 s, MMR 2.18 s; 1.13 s per run overall.
- Projected full matrices at 10 seeds, from the sweep wall clocks: EXP-001 287 s, EXP-002 307 s, EXP-003 374 s; about 16 minutes in total (about 32 minutes at 20 seeds), against the 4-hour budget.
- Seed spread: in the primary contrast (similarity minus random, H_exp, primary cell) the SD of paired differences over 10 seeds is 0.0022 (rule threshold 0.07), so n = 10 meets protocol section 6. Largest H_exp contrast SD: 0.0075 (popularity minus random).
- Degenerate cases: (1) at alpha_0 = 1.0, eta = 0 the observed like rate is about 0.02 for every arm and relevance about 0.10, so feedback is almost all dislikes; at eta = 0.2 the like rate is about 0.21, mostly flips. (2) The random arm's user-control value is about -0.089, not 0. (3) Under the Zipf catalog the random arm's H_exp (about 0.863) is below the similarity arm's (about 0.965). No NaN, no invariant failure, no failed run. Proposed amendments P1 to P5 are in `research/decision_log.md` D-008; the protocol files were not changed.

### Decisions
D-006 (tie rounding), D-007 (operational clarifications, owner review), D-008 (proposed amendments, owner decision).

### Files changed
New: `src/pulse/{config,model,rankers,simulate,metrics,stats,schema,manifest,runner,report,cli}.py`, four test files, `experiments/EXP-00{1,2,3}.json`, `experiments/exploratory/*.json`, `results/exploratory/**`. Modified: `src/pulse/__init__.py` (0.1.0), `pyproject.toml` (version, pytest pythonpath), `uv.lock`, `tests/test_toolchain_smoke.py`, `CONTRIBUTING.md` (commands), `experiments/README.md`, `results/README.md`, `roadmap.md`, `research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv}`.

### Not done
- No confirmatory run and no protocol freeze (G-FREEZE). No experiment report.md (no experiment has run confirmatorily). No demo (M5). Nothing pushed.
- Manuscript untouched: no result to report.

### Outstanding risks
- P1: under the draft calibration the primary contrast is likely to be near zero in the primary cell for reasons of model calibration; the owner should decide before freezing, knowing the exploratory value was seen.
- Peak memory is process-wide, not per run.

### Next action
Owner: decide on D-007 and D-008 (P1 first), then freeze. Session after the freeze: M3 confirmatory runs with `pulse.cli run --experiment EXP-00N`.

## 2026-11-24: data and freeze session, round 2 (MovieLens 1M, amendments, G-FREEZE)

**Milestone:** M1 freeze. **Authority:** owner approvals 2026-11-24 (second round, sections 1 and 7) and the shared DATA-FREEZE and FREEZE briefs.

### Starting state
`git status`: branch main, clean, HEAD df010cd.

### Commands and actual outputs
- Licence check: `curl https://files.grouplens.org/datasets/movielens/ml-1m-README.txt` (research use; no endorsement; cite Harper and Konstan 2015; no redistribution without permission; no commercial use). Matches the approval; adopted (D-009). `curl -I .../ml-1m.zip`: Content-Length 5917549.
- `python scripts/download_movielens.py`: ml-1m.zip 5,917,549 bytes, SHA-256 a6898adb...2c54e20; README 5,576 bytes, 908ee4aa...460027e; hashes pinned; rerun "verified".
- Protocol section 15 (method) written and committed as a15ec6d before any rating was read.
- Code and tests committed as 718e995. First suite run with the new tests: "1 failed, 123 passed" (a test config had pool_size > n_items; test fixed); then "124 passed".
- `.venv/bin/python scripts/prepare_movielens.py` (twice, identical output hashes): 3,883 movies, 0 bad rows, 212 excluded (no top-10 genre); 1,000,209 ratings, 0 bad rows, 22,128 excluded; 3,020 users per half; L* = 0.577143.
- `.venv/bin/python scripts/calibrate_choice_curve.py` at clean 718e995: c(0.1) = 0.066421, c(0.3) = 0.005990, c_ML(0.1) = 0.061067 (2.5 s). A first run at a dirty tree gave identical values. Journal CAL-ML1M.
- Content commit a25d409, then `research/freeze.json`, registry and records.
- `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`: "Audited 6 packages". `.venv/bin/python -m pytest -q`: "135 passed" (no skips; the EXP-004 world test used the local processed file).
- Guard check: `protocol_frozen` returns (True, "frozen") for EXP-001 to EXP-004 with the frozen configs, and refuses each when the seed count is changed.

### Decisions
D-009 (MovieLens adopted), D-010 (method before fit), D-011 (fitted values), D-012 (freeze).

### Not done
- No confirmatory run, no simulation of any arm under the new calibration, no push.
- EXP-001 to EXP-003 reproduction-command text left as frozen (not in the approved list); working commands in EXP-004 section 15 and in the freeze record.
- Exploratory configs keep the planning midpoint; their recorded config hashes no longer match the current SimConfig hash (new fields), values unchanged.

### Risks
- EXP-004 depends on git-ignored files; the run machine must run the download and prepare scripts (hash-checked).
- The SD of paired differences under the new calibration is unknown; 20 seeds fixed by the owner.

### Next action
Coordinator: schedule M3 (`PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-00N`).

## 2026-11-25: M3 session (confirmatory runs of the frozen matrices)

**Milestone:** M3. **Authority:** the owner's "Start next" (2026-11-25) and the coordinator's M3 brief. **Next bounded task at start:** verify the freeze, environment and data, smoke-run, then run EXP-001 to EXP-004 in full.

### Starting state
`git status`: branch main, clean, HEAD 7e4aeba. Every SHA-256 in `research/freeze.json` matched the files on disk.

### Commands and actual outputs
- `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`: "Audited 6 packages". `.venv/bin/python -m pytest -q`: "135 passed". The package is not installed in the venv; every run uses `PYTHONPATH=src` at the checked-out revision.
- `.venv/bin/python scripts/download_movielens.py`: existing zip verified (SHA-256 a6898adb...), no download. `shasum -a 256 data/processed/ml1m_prefs_heldout.json`: 75f9fb8f... (matches the EXP-004 config).
- Analysis code for the frozen decision rules, the EXP-003 Welch interaction, the EXP-002 drift-form rule and per-run provenance (`src/pulse/analysis.py`, `scripts/analyse_experiment.py`, `tests/test_analysis.py`, D-013), tested end to end on stub results: "153 passed". Committed as f1838f3 before any confirmatory run; this is the provenance revision.
- Smoke (exploratory seeds 900001 to 900002): `pulse.cli smoke --out results/exploratory/m3-smoke`: 10 runs ok; metric values identical to the M2 smoke set. Metric validation on known cases: 43 selected golden and property tests passed. Journal XPL-M3-SMOKE and XPL-M3-METRICS.
- Guard: `protocol_frozen` returned (True, "frozen") for all four configs.
- Confirmatory runs, `nice -n 10 env PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-00N`, two at a time, logs in `results/raw/logs/`:

| Experiment | Runs ok / planned | Failed | Wall clock (s) | Peak RSS (bytes) | Primary contrast, mean [95% t] | Frozen rule |
| --- | --- | --- | --- | --- | --- | --- |
| EXP-001 | 480/480 | 0 | 904.6 | 132562944 | H_exp similarity - random -0.4000 [-0.4028, -0.3972] | H1 supported |
| EXP-002 | 480/480 | 0 | 828.2 | 140099584 | Delta H_pref similarity - random -0.4350 [-0.4387, -0.4313] | H1 supported; drift-form rule not met |
| EXP-003 | 240/240 | 0 | 252.2 | 151076864 | Zipf, tau 0.1: -0.5060 [-0.5169, -0.4951] | H1 supported in all 4 cells; invalidation criteria not met; no sign reversal |
| EXP-004 | 60/60 | 0 | 72.4 | 151748608 | H_exp similarity - random -0.4095 [-0.4210, -0.3980] | H1 supported; no sign reversal |

  All runs at f1838f3, clean tree. Total confirmatory wall clock 2026-11-24T23:33:55Z to 23:53:26Z (about 19.5 minutes, budget 4 hours).
- `PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-00N` and `scripts/report_tables.py EXP-00N` for each experiment: verdict, contrasts, provenance, tables and figures written to `research/experiments/EXP-00N/`.
- Final suite: "153 passed".

### Decisions
D-013 (analysis code before data), D-014 (execution record).

### Failures and deviations
- No run failed; no deviation from the frozen protocols.
- The four standalone experiment reports (`research/experiments/EXP-00N/report.md`) were not written: the file tool refused to create them, and the coordinator instructed not to work around it. M3 is not marked done.
- Found after the results: the EXP-002 drift-form check is close to a reparametrisation of gamma (limitations 12).

### Files changed
New: `src/pulse/analysis.py`, `scripts/analyse_experiment.py`, `scripts/report_tables.py`, `tests/test_analysis.py`, `results/raw/EXP-00{1,2,3,4}/` and `results/raw/logs/` (force-added, 4.0 MB), `results/exploratory/m3-smoke/`, `research/experiments/EXP-00N/{verdict.json, metrics.csv, summary.csv, contrasts.csv, run_manifest.json, runs.csv, config.json, tables.md, figures/}`. Modified: `research/{experiment_journal.jsonl, experiment_registry.csv, claims_register.csv (CLM-001 to CLM-008), limitations.md (items 12 to 16), decision_log.md}`, `roadmap.md`.

### Risks
- The primary results were expected by construction; their value is the effect sizes and the sensitivity results.
- The confirmatory Zipf result differs in sign from the pre-freeze exploratory sweep (different calibration); this must be reported prominently in M4 (limitations 15).

### Next action
The owner or the coordinator: decide how the 11.3 experiment reports get written (the file tool refused them in this session). Then M4: evidence audit, second review pass against the preferred hypothesis, manuscript synthesis.
