<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# experiments/

Runnable experiment configurations (JSON) consumed by `pulse.cli`. The research documentation for each experiment (protocol, report, manifest) lives in `research/experiments/EXP-NNN/`.

- `EXP-001.json` to `EXP-004.json`: confirmatory matrices of the frozen protocol v1.0 (2026-11-24): 480, 480, 240 and 60 runs, 20 seeds each (101001+, 102001+, 103001+, 104001+), with the fitted choice-curve midpoints (protocol section 15.11). `pulse.cli run` accepts them only while their files, the protocols and `data/manifest.json` match `research/freeze.json`, and the config passed matches the frozen canonical config. EXP-004 needs the git-ignored MovieLens files (`scripts/download_movielens.py`, then `scripts/prepare_movielens.py`).
- `exploratory/`: exploratory configs only. Their seed ranges (900001+ and up) are disjoint from every confirmatory range, and their outputs go to `results/exploratory/`. Never pooled with confirmatory runs, never findings. They predate the round-2 calibration and keep the planning midpoint 0.5 (the default); because new config fields were added, their config hashes now differ from those recorded in their run files, while their values are unchanged.
  - `smoke.json`: the protocol section 9 smoke matrix (5 arms, 2 seeds, U = 50, N = 300, T = 60, W = 20).
  - `var-probe.json`: full-size EXP-001 primary cell, 5 arms, 10 seeds, to estimate the SD of paired differences (protocol section 6 seed rule) and runtime.
  - `sweep-EXP-00N.json`: every cell of each draft matrix at full size with 2 seeds, for runtime projection and degenerate-case detection.
