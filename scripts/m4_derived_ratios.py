# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Derived ratio used in the manuscript: share of the similarity loss recovered by MMR (descriptive).

recovery = (MMR minus similarity) / -(similarity minus random), per cell, from the point estimates in
research/experiments/EXP-00N/contrasts.csv (metric h_exp for EXP-001, EXP-003, EXP-004; delta_h_pref
for EXP-002). A ratio of two means; no interval is computed and none is claimed.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_derived_ratios.py  (writes results/derived/mmr_recovery.csv)
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    rows = []
    for exp, metric in (("EXP-001", "h_exp"), ("EXP-002", "delta_h_pref"), ("EXP-003", "h_exp"), ("EXP-004", "h_exp")):
        d = {}
        with open(ROOT / "research" / "experiments" / exp / "contrasts.csv") as fh:
            for r in csv.DictReader(fh):
                if r["metric"] == metric:
                    d[(r["cell"], r["treatment"], r["control"])] = float(r["mean_diff"])
        for (cell, t, c), v in sorted(d.items()):
            if t == "mmr" and c == "similarity":
                loss = d[(cell, "similarity", "random")]
                rows.append({"exp_id": exp, "cell": cell, "metric": metric, "similarity_minus_random": loss,
                             "mmr_minus_similarity": v, "recovery_share": v / -loss})
    out = ROOT / "results" / "derived" / "mmr_recovery.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r["exp_id"], r["cell"], f"{r['recovery_share']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
