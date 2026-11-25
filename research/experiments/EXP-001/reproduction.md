<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-001 reproduction

**Label: CONFIRMATORY.** Provenance revision `f1838f3e8451c8c4275579a5736fe488354a8f3a`. Config `experiments/EXP-001.json` (canonical SHA-256 `e51281119eed3c3bcd8ce8042cadc37b104c9b670d4992574e1d2b1095b7afcc`). 480 runs, seeds 101001 to 101020.

## Environment

```
cd pulse-feed-ranking
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q          # 153 passed at the time of the M3 runs
```

Python 3.12.1 and numpy 2.3.5 (`uv.lock`). Run with `PYTHONPATH=src`; the package is not installed in the venv, so the code always comes from the checked-out revision.

## Run

```
git checkout f1838f3e8451c8c4275579a5736fe488354a8f3a
nice -n 10 env PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-001 --out <new empty directory>
```

- The run guard checks every hash in `research/freeze.json` before the first run. It refuses changed protocols, configs or data manifests.
- The runner refuses to write into a directory that already holds results.
- The original run took 904.6 s on an Apple M1 Pro, in parallel with EXP-002.

## Analysis, tables and figures

```
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-001 [RAW_DIR DEST_DIR]
PYTHONPATH=src .venv/bin/python scripts/report_tables.py EXP-001 > research/experiments/EXP-001/tables.md
```

- `analyse_experiment.py` writes `verdict.json`, `metrics.csv`, `summary.csv`, `contrasts.csv`, `run_manifest.json`, `runs.csv`, `config.json` and `figures/`.
- With no directory arguments, it reads `results/raw/EXP-001` and writes into `research/experiments/EXP-001`.

## Checks

- **Raw files.** Compare the SHA-256 of each raw file with `run_manifest.json` (`raw_sha256`).
- **Expected tolerance.** The simulation is seeded, so the same platform and numpy version are expected to give identical metrics. Other platforms may differ in the last floating-point digits.
- **Reference values.** Primary contrast -0.4000, 95% t-interval [-0.4028, -0.3972] (`verdict.json`).
- **Data.** No real data file is read. The data manifest `data/manifest.json` must have SHA-256 `296b1edc9522d06275b20fc29fae08b0fc0405f880cf81fc9174ee26699a9fc0`.
