# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Summary table and figure of the M4 exploratory like-rate check (XPL-M4-LIKERATE). EXPLORATORY ONLY.

Reads results/exploratory/m4-likerate-{uniform,zipf}/report/{contrasts.csv,summary.csv} (written by
`pulse.cli report --no-pdf` from the run files) and results/exploratory/m4-likerate-fit.json.
Writes results/exploratory/m4-likerate-summary.csv and research/paper/figures/FIG-M4-X01.svg.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_likerate_summary.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse.analysis import forest_svg  # noqa: E402

ETA = 0.1  # feedback noise of the check; observed like rate = eta + (1 - 2 eta) * true like rate


def main() -> int:
    fit = json.loads((ROOT / "results" / "exploratory" / "m4-likerate-fit.json").read_text())
    target = {lv["like_midpoint"]: lv for lv in fit["levels"]}
    rows, fig = [], []
    for skew in ("uniform", "zipf"):
        rep = ROOT / "results" / "exploratory" / f"m4-likerate-{skew}" / "report"
        summ = {(r["cell"], r["arm"]): r for r in csv.DictReader(open(rep / "summary.csv"))}
        con = [r for r in csv.DictReader(open(rep / "contrasts.csv"))
               if r["metric"] == "h_exp" and r["treatment"] == "similarity" and r["control"] == "random"]
        con.sort(key=lambda r: -float(r["cell"].split("=")[1]))
        for r in con:
            c = float(r["cell"].split("=")[1])
            lv = next(v for k, v in target.items() if abs(k - c) < 1e-15)
            obs = float(summ[(r["cell"], "random")]["like_rate_mean"])
            rows.append({
                "pool_skew": skew, "like_midpoint": c,
                "fitted_target_true_like_rate_uniform_world": lv["achieved"],
                "random_observed_like_rate": obs,
                "random_implied_true_like_rate": (obs - ETA) / (1 - 2 * ETA),
                "random_h_exp": float(summ[(r["cell"], "random")]["h_exp_mean"]),
                "similarity_h_exp": float(summ[(r["cell"], "similarity")]["h_exp_mean"]),
                "n_seeds": int(r["n"]), "delta_mean": float(r["mean_diff"]), "delta_sd": float(r["sd_diff"]),
                "t_lo": float(r["t_lo"]), "t_hi": float(r["t_hi"])})
            fig.append({"label": f"{skew}, target like rate {lv['achieved']:.3f}", "mean": float(r["mean_diff"]),
                        "lo": float(r["t_lo"]), "hi": float(r["t_hi"])})
    out = ROOT / "results" / "exploratory" / "m4-likerate-summary.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    svg = forest_svg(fig, "FIG-M4-X01 (EXPLORATORY): similarity minus random in H_exp vs target like rate, 5 seeds",
                     "Delta H_exp (unitless); bar = 95% paired t-interval; dashed = -0.05")
    (ROOT / "research" / "paper" / "figures" / "FIG-M4-X01.svg").write_text(svg)
    print(out)
    for r in rows:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
