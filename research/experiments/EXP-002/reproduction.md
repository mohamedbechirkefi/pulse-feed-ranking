<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-002 reproduction

**Label: CONFIRMATORY.** Provenance revision `f1838f3e8451c8c4275579a5736fe488354a8f3a`. Config `experiments/EXP-002.json` (canonical SHA-256 `2c3b1816328f95d487bd83c1002a6db3970881a0eed91a2677569c3f2cfeed59`). 480 runs, seeds 102001 to 102020.

## Environment

```
uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q
```

## Run

```
git checkout f1838f3e8451c8c4275579a5736fe488354a8f3a
nice -n 10 env PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-002 --out <new empty directory>
```

The run guard verifies the frozen hashes first. The original run took 828.2 s on an Apple M1 Pro, in parallel with EXP-001.

## Analysis, tables and figures

```
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-002 [RAW_DIR DEST_DIR]
PYTHONPATH=src .venv/bin/python scripts/report_tables.py EXP-002 > research/experiments/EXP-002/tables.md
```

## Checks

- **Raw files.** Compare the SHA-256 of each raw file with `run_manifest.json` (`raw_sha256`).
- **Reference values.** Primary contrast -0.4350, 95% t-interval [-0.4387, -0.4313]. Drift-form D: -0.4363 (alpha_0 1.0) and -0.4351 (alpha_0 0.1) (`verdict.json`).
- **Tolerance.** Identical values are expected on the same platform and numpy version. Other platforms may differ in the last floating-point digits.
