# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Fit the choice-curve midpoints (protocol sections 15.5 and 15.6). Exploratory fit, journaled.

Inputs: data/processed/ml1m_summary.json (L*, pi_ML) and ml1m_prefs_calibration.json.
Output: results/calibration/calibration.json (aggregates only; committed).
Uses only the catalog and user generators: no ranker, no simulation loop, no metric.

Usage: python scripts/calibrate_choice_curve.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse.calibrate import BRACKET, CALIBRATION_SEEDS, TOL, file_users, fit_midpoint, mean_like, utilities  # noqa: E402
from pulse.config import SimConfig  # noqa: E402
from pulse.manifest import environment, git_revision  # noqa: E402
from pulse.model import load_preference_file  # noqa: E402

PROC = ROOT / "data" / "processed"
OUT = ROOT / "results" / "calibration" / "calibration.json"


def main() -> int:
    t0 = time.perf_counter()
    summary = json.loads((PROC / "ml1m_summary.json").read_text())
    target = summary["like_rate_calibration_L_star"]
    pi = summary["pi_ml"]
    s = sum(pi)
    pi = [w / s for w in pi]
    fits = {}
    base = SimConfig()  # section 2 defaults: uniform pool, alpha0 = 1.0, K = 10, U = 200, N = 1000
    rs = utilities(base, CALIBRATION_SEEDS)
    for tau in (0.1, 0.3):
        c = fit_midpoint(rs, tau, target)
        fits[f"synthetic_tau{tau}"] = {"tau": tau, "like_midpoint": c, "achieved_mean_like": mean_like(rs, tau, c),
                                       "planning_midpoint_mean_like": mean_like(rs, tau, 0.5),
                                       "users": "Dirichlet(1.0)", "catalog": "uniform"}
    h_cal = summary["files"]["ml1m_prefs_calibration.json"]
    V = load_preference_file("data/processed/ml1m_prefs_calibration.json", h_cal, str(ROOT))
    ml_cfg = SimConfig(pool_skew="custom", topic_weights=pi)
    rs_ml = utilities(ml_cfg, CALIBRATION_SEEDS, users=file_users(V))
    c = fit_midpoint(rs_ml, 0.1, target)
    fits["movielens_tau0.1"] = {"tau": 0.1, "like_midpoint": c, "achieved_mean_like": mean_like(rs_ml, 0.1, c),
                                "planning_midpoint_mean_like": mean_like(rs_ml, 0.1, 0.5),
                                "users": "calibration-half vectors (sampled 200 per seed without replacement)",
                                "catalog": "custom pi_ML"}
    out = {
        "label": "exploratory (calibration fit, protocol section 15.5 and 15.6)",
        "target_like_rate_L_star": target,
        "pi_ml": pi,
        "topics": summary["topics"],
        "calibration_seeds": [CALIBRATION_SEEDS[0], CALIBRATION_SEEDS[-1]],
        "bracket": list(BRACKET), "tolerance": TOL,
        "fits": fits,
        "inputs_sha256": {"ml1m_summary.json": hashlib.sha256((PROC / "ml1m_summary.json").read_bytes()).hexdigest(),
                          **summary["files"]},
        "source_zip_sha256": summary["source_zip_sha256"],
        "code_revision": git_revision(),
        "environment": environment(),
        "wall_clock_s": round(time.perf_counter() - t0, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("target_like_rate_L_star", "fits", "wall_clock_s")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
