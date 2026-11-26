<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# demo/: PULSE interactive research page (M5)

A static page that runs offline after the first load. It has no backend, no account, no analytics and no request to any other host, and it collects nothing about visitors.

## What it shows

- **Published results** from `public/data/results.json`, written by `scripts/export_demo_data.py` from committed result files only and printed exactly as in `research/paper/manuscript.md` (checked by `tests/test_demo_export.py`). Every registered experiment appears with its status and verdict: EXP-001 to EXP-004 (measured, confirmatory), the exploratory like-rate check XPL-M4-LIKERATE and the pre-freeze probe (measured, exploratory), and EXP-005 (registered, not frozen, not run; no estimate). Each estimate is shown with its 95% interval and an interval glyph. The loader validates the file and fails closed: if anything is missing or malformed, no number is shown.
- **Figures from the exported data:** the measured EXP-001 exposure heatmap (mean H_exp and SD by ranker and cell) and the exploratory like-rate boundary chart.
- **Assumptions** (model inputs, labelled as such) and **method and limitations**.
- **Sandbox (illustrative, not the research engine):** two simulated feeds side by side with topic cards, a preference timeline, an exposure timeline, exposure heatmaps and run metrics, with seed, ranker, preference model, catalog, feedback noise and choice-curve controls, plus Run, Cancel and Reset. It runs in a Web Worker (`src/sandbox.worker.ts`) on a TypeScript port of the PULSE loop, rankers and metrics (`src/engine.ts`). `src/engine.test.ts` replays random inputs recorded from the Python engine (`scripts/export_sandbox_fixture.py`) and requires identical slates and metrics within 1e-9. In the browser the random numbers come from a different generator (mulberry32, not numpy) and the world is smaller (60 users, 300 items, pools of 30, 120 steps), so sandbox output never reproduces a research run and is not comparable with the published numbers. Each run is bounded; there is no autoplay, endless feed, score or reward.

## Commands

Node 22 and npm. From this folder:

    npm ci && npm run build && npm run preview     # build and serve the static page locally
    npm test                                        # vitest: results validator and engine parity
    node tools/a11y_check.mjs dist --screenshots <dir>   # offline and accessibility smoke check (needs Google Chrome)

To refresh the data after a change in committed results: `.venv/bin/python scripts/export_demo_data.py` from the repository root, then rebuild. Dependencies are pinned in `package-lock.json`; `.npmrc` disables install scripts.

## Hosting

The built page (`dist/`) is hosted at https://pulse-feed-ranking.kefimohamedbechir.workers.dev as Cloudflare Workers static assets on the free plan, configured by `wrangler.jsonc` (assets only, no Worker script). It is deployed by the coordinator of the research workspace, not by any script of this repository. The hosted page makes no request to any other host (checked by `tools/a11y_check.mjs`).

Repository: https://github.com/mohamedbechirkefi/pulse-feed-ranking

## Brand, type and third-party notes

The page has its own identity, the broadcast control room (plan and review in `DESIGN.md`). Brand files are in `public/brand/`: the mark (`pulse-mark.svg`, with `-mono` and `-on-dark` versions), the lockup (`pulse-lockup.svg`, with `-light`, `-mono` and `-on-dark` versions), `favicon.svg`, `favicon-32.png` and the Open Graph image `og.png` (1200 by 630). The mark is drawn by hand as paths; the wordmark is outlined from Archivo by `tools/build_logo.py`.

Fonts, self-hosted from Fontsource packages pinned in `package-lock.json` (Latin subset only, declared in `src/fonts.css`):

- Archivo Variable, package `@fontsource-variable/archivo` v5.3.0, SIL Open Font License v1.1 (display, interface and tabular figures).
- Source Serif 4 Variable, package `@fontsource-variable/source-serif-4` v5.3.1, SIL Open Font License v1.1 (reading text).
