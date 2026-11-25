# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""M4 exploratory check XPL-M4-LIKERATE: does the primary contrast depend on the target like rate?

EXPLORATORY ONLY. Never pooled with confirmatory runs; never changes a frozen verdict.

Motivation (research/publication/review_pass_2.md, research/freeze.json c4_disclosure): under the
planning midpoint 0.5 (like rate about 0.02) the exploratory primary contrast was about -0.0007, while
under the frozen calibration (like rate 0.577) it is -0.4000. This script fits, with the frozen
calibration method (protocol section 15.5: same generators, same calibration seeds 700001 to 700020,
same bisection), one midpoint per target like rate at tau 0.1 on the uniform synthetic world, and
writes two exploratory configs (uniform and Zipf catalogs) that cross the midpoint with the arms
random and similarity. The other settings are those of the EXP-003 tau0.1 block (eta 0.1,
alpha_0 1.0, static). As in the frozen design, the midpoint fitted on the uniform world is also used
under Zipf, so the Zipf like rates differ from the targets; they are reported as observed.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_likerate_configs.py
Then:  PYTHONPATH=src .venv/bin/python -m pulse.cli run --config experiments/exploratory/m4-likerate-uniform.json
       PYTHONPATH=src .venv/bin/python -m pulse.cli run --config experiments/exploratory/m4-likerate-zipf.json
       PYTHONPATH=src .venv/bin/python -m pulse.cli report --results results/exploratory/m4-likerate-<skew> --no-pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse.calibrate import CALIBRATION_SEEDS, fit_midpoint, mean_like, utilities  # noqa: E402
from pulse.config import SimConfig  # noqa: E402

TAU = 0.1
TARGETS = (0.05, 0.15, 0.30, 0.45, 0.5771428687720555, 0.70, 0.85)  # 0.577... is the frozen L*
PLANNING_MIDPOINT = 0.5  # the pre-freeze value (like rate about 0.02)
SEEDS = {"first": 960001, "count": 5}  # disjoint from every confirmatory and earlier exploratory range


def main() -> int:
    rs = utilities(SimConfig(), CALIBRATION_SEEDS)
    levels = []
    for t in TARGETS:
        c = fit_midpoint(rs, TAU, t)
        levels.append({"target": t, "like_midpoint": c, "achieved": mean_like(rs, TAU, c)})
    levels.append({"target": None, "like_midpoint": PLANNING_MIDPOINT,
                   "achieved": mean_like(rs, TAU, PLANNING_MIDPOINT)})
    fit_path = ROOT / "results" / "exploratory" / "m4-likerate-fit.json"
    fit_path.parent.mkdir(parents=True, exist_ok=True)
    fit_path.write_text(json.dumps({
        "label": "exploratory (XPL-M4-LIKERATE midpoint fits; frozen method of protocol section 15.5)",
        "tau": TAU, "calibration_seeds": [CALIBRATION_SEEDS[0], CALIBRATION_SEEDS[-1]],
        "world": "uniform catalog, Dirichlet(1.0) users, section 2 defaults", "levels": levels}, indent=1) + "\n")
    for skew in ("uniform", "zipf"):
        exp = {
            "experiment_id": f"XPL-M4-LIKERATE-{skew.upper()}",
            "label": "exploratory",
            "description": ("M4 exploratory like-rate sensitivity of the primary contrast (not a confirmatory "
                            "experiment; never pooled; never changes a frozen verdict). Settings of the EXP-003 "
                            "tau0.1 block, midpoint crossed as a factor, 5 seeds 960001+."),
            "output_dir": f"results/exploratory/m4-likerate-{skew}",
            "base": {"n_users": 200, "n_items": 1000, "n_topics": 10, "pool_size": 50, "slate_size": 10,
                     "n_steps": 200, "window": 50, "preference_model": "static", "eta": 0.1, "alpha0": 1.0,
                     "zipf_s": 1.0, "pool_skew": skew, "tau": TAU},
            "seeds": SEEDS,
            "blocks": [{"name": "likerate",
                        "factors": {"like_midpoint": [lv["like_midpoint"] for lv in levels]},
                        "arms": [{"arm": "random", "ranker": "random"},
                                 {"arm": "similarity", "ranker": "similarity"}]}],
        }
        p = ROOT / "experiments" / "exploratory" / f"m4-likerate-{skew}.json"
        p.write_text(json.dumps(exp, indent=1) + "\n")
        print(p)
    for lv in levels:
        print(lv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
