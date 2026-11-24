<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# experiments/

Runnable experiment configurations (JSON) consumed by `pulse.cli`. The research documentation for each experiment (protocol, report, manifest) lives in `research/experiments/EXP-NNN/`.

- `EXP-001.json`, `EXP-002.json`, `EXP-003.json`: confirmatory matrices transcribed from the draft protocols v0.1 (240, 240 and 120 runs; confirmatory seed ranges 101001+, 102001+, 103001+). `pulse.cli run` refuses them until the owner freezes the protocol (G-FREEZE) and the registry carries a matching SHA-256.
- `exploratory/`: exploratory configs only. Their seed ranges (900001+ and up) are disjoint from every confirmatory range, and their outputs go to `results/exploratory/`. Never pooled with confirmatory runs, never findings.
  - `smoke.json`: the protocol section 9 smoke matrix (5 arms, 2 seeds, U = 50, N = 300, T = 60, W = 20).
  - `var-probe.json`: full-size EXP-001 primary cell, 5 arms, 10 seeds, to estimate the SD of paired differences (protocol section 6 seed rule) and runtime.
  - `sweep-EXP-00N.json`: every cell of each draft matrix at full size with 2 seeds, for runtime projection and degenerate-case detection.
