# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Frozen confirmatory analysis (protocol v1.0): verdicts, interactions, provenance, figures.

Written and committed before any confirmatory output existed (M3, 2026-11-25). It encodes the
decision rules of the frozen protocols; it never chooses a test, a cell or a threshold from data.

Rules encoded (protocol sections 3, 15.6, 15.9; EXP protocols section 5 and 14):

- Primary rule (EXP-001, EXP-002, EXP-004, and every EXP-003 cell): with Delta the mean paired
  difference treatment minus control and [lo, hi] its 95% paired t-interval over seeds,
  H1 (Delta < 0) is supported only if hi < 0 and Delta <= -0.05 (smallest effect of interest).
  Otherwise the contradiction rule is met, with one of three reasons: "sign reversal" (lo > 0),
  "interval includes 0" (lo <= 0 <= hi), or "no practically relevant reduction" (hi < 0 but
  Delta > -0.05). "Sign reversal" triggers the pre-decided reporting rule of section 15.9 where it
  applies (Zipf cells of EXP-003, EXP-004).
- EXP-003 invalidation (EXP-003 section 5): the skew criterion is met if, in a Zipf cell, the 95%
  interval includes 0, lies above 0, or the point estimate is above -0.05; it is evaluated in both
  Zipf cells (tau 0.1 is the designated primary cell). The sharpness criterion ("likewise for
  tau = 0.3") is evaluated in the same way in both tau = 0.3 cells.
- EXP-003 interaction (section 6 and 8): per tau block, (mean Delta under Zipf) minus (mean Delta
  under uniform), Welch t-interval with Welch-Satterthwaite degrees of freedom, seeds as units.
- EXP-002 drift-form check (section 14): D under additive-then-clip versus D under the
  multiplicative rule at gamma = 0.05, per alpha_0; reinforcement is reported as dependent on the
  drift form if the sign of the point estimate changes or |D| under the check falls below 0.05.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from .manifest import REPO_ROOT
from .stats import paired_summary, t_ppf

SESOI = 0.05


def primary_verdict(mean: float, lo: float, hi: float, sesoi: float = SESOI) -> dict:
    """Frozen decision rule for a directional H1 (Delta < 0)."""
    if hi < 0 and mean <= -sesoi:
        return {"h1_supported": True, "contradiction": False, "reason": "H1 supported"}
    if lo > 0:
        reason = "sign reversal"
    elif hi >= 0:
        reason = "interval includes 0"
    else:
        reason = "no practically relevant reduction"
    return {"h1_supported": False, "contradiction": True, "reason": reason}


def welch_interval(x, y, level: float = 0.95) -> dict:
    """Mean(x) - mean(y) with a Welch t-interval (unpaired, unequal variances)."""
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if a.size < 2 or b.size < 2:
        raise ValueError("Welch interval needs at least two values per group")
    va, vb = a.var(ddof=1) / a.size, b.var(ddof=1) / b.size
    diff = float(a.mean() - b.mean())
    se = math.sqrt(va + vb)
    if se == 0:
        return {"diff": diff, "se": 0.0, "df": None, "lo": diff, "hi": diff}
    df = (va + vb) ** 2 / (va ** 2 / (a.size - 1) + vb ** 2 / (b.size - 1))
    half = t_ppf(0.5 + level / 2, df) * se
    return {"diff": diff, "se": se, "df": df, "lo": diff - half, "hi": diff + half}


def _cell_of(r: dict) -> tuple:
    return (r["block"], tuple(sorted(r["cell"].items())))


def per_seed(results: list[dict], block: str, cell: dict, arm: str, metric: str) -> dict[int, float]:
    key = (block, tuple(sorted(cell.items())))
    return {r["seed"]: r["metrics"][metric] for r in results
            if r["status"] == "ok" and _cell_of(r) == key and r["arm"] == arm}


def paired_deltas(results, block, cell, treat, control, metric) -> tuple[list[int], list[float]]:
    a = per_seed(results, block, cell, treat, metric)
    b = per_seed(results, block, cell, control, metric)
    seeds = sorted(set(a) & set(b))
    return seeds, [a[s] - b[s] for s in seeds]


def contrast(results, block, cell, treat, control, metric) -> dict:
    a = per_seed(results, block, cell, treat, metric)
    b = per_seed(results, block, cell, control, metric)
    seeds = sorted(set(a) & set(b))
    ps = paired_summary([a[s] for s in seeds], [b[s] for s in seeds]).to_dict()
    return {"block": block, "cell": cell, "treatment": treat, "control": control, "metric": metric,
            "seeds": seeds, **ps}


def with_verdict(c: dict) -> dict:
    return {**c, **primary_verdict(c["mean_diff"], c["t_lo"], c["t_hi"])}


def analyse_exp001(results: list[dict]) -> dict:
    cells = [{"eta": e, "alpha0": a} for e in (0.0, 0.2) for a in (1.0, 0.1)]
    prim = with_verdict(contrast(results, "main", {"eta": 0.0, "alpha0": 1.0}, "similarity", "random", "h_exp"))
    sec = [with_verdict(contrast(results, "main", c, "similarity", "random", "h_exp")) for c in cells
           if c != {"eta": 0.0, "alpha0": 1.0}]
    return {"experiment_id": "EXP-001", "primary": prim, "secondary_cells": sec}


def analyse_exp002(results: list[dict]) -> dict:
    m = "delta_h_pref"
    prim = with_verdict(contrast(results, "main", {"gamma": 0.05, "alpha0": 1.0}, "similarity", "random", m))
    cells = [{"gamma": g, "alpha0": a} for g in (0.01, 0.05) for a in (1.0, 0.1)]
    sec = [with_verdict(contrast(results, "main", c, "similarity", "random", m)) for c in cells
           if c != {"gamma": 0.05, "alpha0": 1.0}]
    drift = []
    for a0 in (1.0, 0.1):
        base = contrast(results, "main", {"gamma": 0.05, "alpha0": a0}, "similarity", "random", m)
        chk = contrast(results, "driftform", {"alpha0": a0}, "similarity", "random", m)
        sign_change = (math.copysign(1, base["mean_diff"]) != math.copysign(1, chk["mean_diff"]))
        small = abs(chk["mean_diff"]) < SESOI
        drift.append({"alpha0": a0, "D_multiplicative": base["mean_diff"], "D_additive_clip": chk["mean_diff"],
                      "check": chk, "sign_change": sign_change, "abs_below_sesoi": small,
                      "dependent_on_drift_form": bool(sign_change or small)})
    return {"experiment_id": "EXP-002", "primary": prim, "secondary_cells": sec, "drift_form": drift}


def analyse_exp003(results: list[dict]) -> dict:
    cells = []
    for block in ("tau0.1", "tau0.3"):
        for skew in ("uniform", "zipf"):
            c = with_verdict(contrast(results, block, {"pool_skew": skew}, "similarity", "random", "h_exp"))
            c["sign_reversal_rule_15_9_applies"] = skew == "zipf" and c["reason"] == "sign reversal"
            c["mmr_minus_similarity"] = contrast(results, block, {"pool_skew": skew}, "mmr", "similarity", "h_exp")
            cells.append(c)
    by = {(c["block"], c["cell"]["pool_skew"]): c for c in cells}
    skew_crit = {b: by[(b, "zipf")]["contradiction"] for b in ("tau0.1", "tau0.3")}
    sharp_crit = {s: by[("tau0.3", s)]["contradiction"] for s in ("uniform", "zipf")}
    inter = []
    for block in ("tau0.1", "tau0.3"):
        _, dz = paired_deltas(results, block, {"pool_skew": "zipf"}, "similarity", "random", "h_exp")
        _, du = paired_deltas(results, block, {"pool_skew": "uniform"}, "similarity", "random", "h_exp")
        inter.append({"block": block, "contrast": "Delta(zipf) - Delta(uniform)", **welch_interval(dz, du)})
    return {"experiment_id": "EXP-003", "primary": by[("tau0.1", "zipf")], "cells": cells,
            "skew_criterion_met": skew_crit, "sharpness_criterion_met": sharp_crit,
            "restricted_to_balanced_pools": any(skew_crit.values()),
            "dependent_on_choice_sharpness": any(sharp_crit.values()), "skew_interaction": inter}


def analyse_exp004(results: list[dict]) -> dict:
    prim = with_verdict(contrast(results, "main", {}, "similarity", "random", "h_exp"))
    prim["sign_reversal_rule_15_9_applies"] = prim["reason"] == "sign reversal"
    return {"experiment_id": "EXP-004", "primary": prim}


ANALYSES = {"EXP-001": analyse_exp001, "EXP-002": analyse_exp002, "EXP-003": analyse_exp003,
            "EXP-004": analyse_exp004}


def _end(start: str, runtime: float) -> str:
    t = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (t + timedelta(seconds=runtime)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _repo_relative(path: Path) -> str:
    """Path relative to the repository root when inside it, so no local home path is recorded (M6, F-7)."""
    try:
        return Path(path).resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def provenance(results_dir: Path, data_manifest_sha256: str, extra_data: dict | None = None) -> dict:
    """Per-run provenance plus SHA-256 of every raw file in the result set (no run dropped)."""
    results_dir = Path(results_dir)
    files = sorted(results_dir.glob("runs/*.json")) + [results_dir / "set_manifest.json",
                                                        results_dir / "result_schema.json"]
    runs = []
    for f in sorted(results_dir.glob("runs/*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        man = r["manifest"]
        runs.append({"run_id": r["run_id"], "config_hash": r["config_hash"], "seed": r["seed"],
                     "revision": man["git"]["commit"], "dirty": man["git"]["dirty"],
                     "data_manifest_sha256": data_manifest_sha256, "hardware": man["cpu"], "os": man["os"],
                     "started_utc": man["started_utc"], "ended_utc": _end(man["started_utc"], man["runtime_s"]),
                     "runtime_s": man["runtime_s"], "status": r["status"]})
    return {"results_dir": _repo_relative(results_dir), "n_runs": len(runs),
            "n_failed": sum(r["status"] != "ok" for r in runs), "data": extra_data or {},
            "raw_sha256": {str(f.relative_to(results_dir)): hashlib.sha256(f.read_bytes()).hexdigest()
                           for f in files if f.exists()},
            "runs": runs}


def write_runs_csv(path: Path, runs: list[dict]) -> None:
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(runs[0]))
        w.writeheader()
        w.writerows(runs)


def forest_svg(rows: list[dict], title: str, xlabel: str, sesoi: float | None = SESOI) -> str:
    """Point estimate and 95% t-interval per row (label, mean, lo, hi); zero and -SESOI marked."""
    vals = [v for r in rows for v in (r["lo"], r["hi"], r["mean"])] + [0.0]
    if sesoi is not None:
        vals.append(-sesoi)
    lo, hi = min(vals), max(vals)
    pad = 0.08 * (hi - lo or 1.0)
    lo, hi = lo - pad, hi + pad
    left, right, top, rowh, width = 330, 40, 50, 24, 900
    height = top + rowh * len(rows) + 60
    pw = width - left - right

    def x(v: float) -> float:
        return left + (v - lo) / (hi - lo) * pw

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
         f'font-family="Helvetica, Arial, sans-serif" font-size="11">',
         f'<rect width="{width}" height="{height}" fill="white"/>',
         f'<text x="{left}" y="22" font-size="13" font-weight="bold">{title}</text>']
    for i in range(6):
        v = lo + i * (hi - lo) / 5
        p.append(f'<text x="{x(v):.1f}" y="{top + rowh * len(rows) + 16}" text-anchor="middle">{v:.3f}</text>')
    yb = top + rowh * len(rows)
    p.append(f'<line x1="{x(0):.1f}" y1="{top - 8}" x2="{x(0):.1f}" y2="{yb}" stroke="#444" stroke-width="1"/>')
    if sesoi is not None:
        p.append(f'<line x1="{x(-sesoi):.1f}" y1="{top - 8}" x2="{x(-sesoi):.1f}" y2="{yb}" stroke="#b33" '
                 f'stroke-dasharray="4 3"/>')
        p.append(f'<text x="{x(-sesoi):.1f}" y="{top - 12}" text-anchor="middle" fill="#b33">-{sesoi}</text>')
    for j, r in enumerate(rows):
        y = top + rowh * j + rowh / 2
        p.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{r["label"]}</text>')
        p.append(f'<line x1="{x(r["lo"]):.1f}" y1="{y:.1f}" x2="{x(r["hi"]):.1f}" y2="{y:.1f}" stroke="#1f5f8b" '
                 f'stroke-width="2"/>')
        p.append(f'<circle cx="{x(r["mean"]):.1f}" cy="{y:.1f}" r="4" fill="#1f5f8b"/>')
    p.append(f'<text x="{left + pw / 2:.1f}" y="{height - 12}" text-anchor="middle">{xlabel}</text>')
    p.append("</svg>")
    return "\n".join(p) + "\n"
