<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-003 reproduction

**Label: CONFIRMATORY.** Provenance revision `f1838f3e8451c8c4275579a5736fe488354a8f3a`. Config `experiments/EXP-003.json` (canonical SHA-256 `4aafb0446e763a37fe78cf83e00d94bdfc65fd5282579e82e5bd2cd1474b934f`). 240 runs, seeds 103001 to 103020.

## Environment

```
uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q
```

## Run

```
git checkout f1838f3e8451c8c4275579a5736fe488354a8f3a
nice -n 10 env PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-003 --out <new empty directory>
```

The original run took 252.2 s on an Apple M1 Pro, in parallel with EXP-004.

## Analysis, tables and figures

```
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-003 [RAW_DIR DEST_DIR]
PYTHONPATH=src .venv/bin/python scripts/report_tables.py EXP-003 > research/experiments/EXP-003/tables.md
```

## Checks

- **Raw files.** Compare the SHA-256 of each raw file with `run_manifest.json`.
- **Reference values (`verdict.json`).** Primary cell (tau 0.1, Zipf) -0.5060 [-0.5169, -0.4951]. Interaction -0.1059 [-0.1170, -0.0948] (tau 0.1) and -0.1503 [-0.1611, -0.1396] (tau 0.3).
- **Tolerance.** Identical values are expected on the same platform and numpy version.
