<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-004 reproduction

**Label: CONFIRMATORY.** Provenance revision `f1838f3e8451c8c4275579a5736fe488354a8f3a`. Config `experiments/EXP-004.json` (canonical SHA-256 `43afda057c89f26add143561edbc0b0033de19675b8b5ef1626103518cdba9b2`). 60 runs, seeds 104001 to 104020.

## Environment

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q
```

## Real data (git-ignored; never committed, GroupLens licence)

```
.venv/bin/python scripts/download_movielens.py    # ml-1m.zip, SHA-256 a6898adb50b9ca05aa231689da44c217cb524e7ebd39d264c56e2832f2c54e20
.venv/bin/python scripts/prepare_movielens.py     # data/processed/ml1m_prefs_heldout.json
shasum -a 256 data/processed/ml1m_prefs_heldout.json
# must be 75f9fb8ffa2a7e6eb14058b69d8d1722862591fd2447065de078415899f8c505; if not, stop (every run fails by design)
```

## Run

```
git checkout f1838f3e8451c8c4275579a5736fe488354a8f3a
nice -n 10 env PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-004 --out <new empty directory>
```

The original run took 72.4 s on an Apple M1 Pro, in parallel with EXP-003.

## Analysis, tables and figures

```
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-004 [RAW_DIR DEST_DIR]
PYTHONPATH=src .venv/bin/python scripts/report_tables.py EXP-004 > research/experiments/EXP-004/tables.md
```

## Checks

- **Raw files.** Compare the SHA-256 of each raw file with `run_manifest.json`.
- **Reference values.** Primary contrast -0.4095, 95% t-interval [-0.4210, -0.3980] (`verdict.json`).
- **Tolerance.** Identical values are expected on the same platform and numpy version.
