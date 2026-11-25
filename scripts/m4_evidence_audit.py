# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""M4 evidence audit (master prompt 11.5): recompute from raw outputs and trace every number.

Part A, raw-output recomputation, independent of src/pulse/stats.py and src/pulse/analysis.py:
  - every raw run file's SHA-256 against research/experiments/EXP-00N/run_manifest.json;
  - run counts per (block, cell, arm), status ok, code revision and dirty flag;
  - every paired contrast in contrasts.csv (n, mean, SD, 95% t-interval) recomputed from the raw
    per-seed metrics, with a t quantile computed here by numerical integration of the t density;
  - the EXP-003 Welch skew interaction and the EXP-002 drift-form values in verdict.json;
  - per-arm means and SDs in summary.csv.
Part C, section-scoped trace of manuscript sections 5.1 to 5.4 and row-wise checks of Table S3 and
Table 7 against their derived files.
Part D, row-wise check of manuscript Tables 2 to 6 against contrasts.csv.
Part B, number trace: every decimal number (two or more decimals) in the reports, the manuscript, the
supplementary file and the claims register must equal, at its printed precision, some numeric value in
a committed evidence file. Numbers without a match are listed for manual review.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py > research/publication/evidence_audit_output.txt
Exit status 0 when Part A has no mismatch; Part B lists are printed for review, not judged here.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXPS = ("EXP-001", "EXP-002", "EXP-003", "EXP-004")
TOL = 1e-9


def t_ppf975(df: float) -> float:
    """0.975 quantile of Student t by bisection on a numerically integrated CDF (independent check)."""
    def cdf(x: float) -> float:
        g = np.linspace(0.0, x, 200001)
        logc = math.lgamma((df + 1) / 2) - math.lgamma(df / 2) - 0.5 * math.log(df * math.pi)
        dens = np.exp(logc - (df + 1) / 2 * np.log1p(g * g / df))
        return 0.5 + float(np.trapezoid(dens, g))
    lo, hi = 0.0, 20.0
    while hi - lo > 1e-12:
        mid = (lo + hi) / 2
        if cdf(mid) < 0.975:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cell_key(r: dict) -> str:
    return r["block"] + ":" + (",".join(f"{k}={v}" for k, v in r["cell"].items()) or "base")


def load_raw(exp: str) -> list[dict]:
    d = ROOT / "results" / "raw" / exp / "runs"
    return [json.loads(p.read_text()) for p in sorted(d.glob("*.json"))]


def part_a() -> list[str]:
    problems: list[str] = []
    tcache: dict[float, float] = {}

    def tq(df: float) -> float:
        if df not in tcache:
            tcache[df] = t_ppf975(df)
        return tcache[df]

    for exp in EXPS:
        edir = ROOT / "research" / "experiments" / exp
        man = json.loads((edir / "run_manifest.json").read_text())
        raw_dir = ROOT / "results" / "raw" / exp
        n_hash = 0  # run files only; the manifest also hashes set_manifest.json and result_schema.json
        for rel, h in man["raw_sha256"].items():
            got = hashlib.sha256((raw_dir / rel).read_bytes()).hexdigest()
            n_hash += rel.startswith("runs/")
            if got != h:
                problems.append(f"{exp}: SHA-256 mismatch {rel}")
        runs = load_raw(exp)
        revs = {(r["manifest"]["git"]["commit"], r["manifest"]["git"]["dirty"]) for r in runs}
        status = defaultdict(int)
        for r in runs:
            status[r["status"]] += 1
        print(f"{exp}: raw files {len(runs)}, hashes checked {n_hash}, manifest n_runs {man['n_runs']}, "
              f"n_failed {man['n_failed']}, status {dict(status)}, revisions {sorted(revs)}")
        if len(runs) != man["n_runs"] or n_hash != len(runs) or status.get("ok", 0) != len(runs):
            problems.append(f"{exp}: run count or status mismatch")
        if revs != {("f1838f3e8451c8c4275579a5736fe488354a8f3a", False)}:
            problems.append(f"{exp}: unexpected revision or dirty tree {revs}")
        by = defaultdict(dict)  # (cell, arm) -> seed -> metrics
        for r in runs:
            by[(cell_key(r), r["arm"])][r["seed"]] = r["metrics"]
        # contrasts.csv
        n_c = 0
        with open(edir / "contrasts.csv") as fh:
            for row in csv.DictReader(fh):
                t, c, m = by[(row["cell"], row["treatment"])], by[(row["cell"], row["control"])], row["metric"]
                seeds = sorted(set(t) & set(c))
                d = np.array([t[s][m] - c[s][m] for s in seeds], dtype=float)
                n = len(d)
                mean, sd = float(d.mean()), float(d.std(ddof=1))
                half = tq(float(n - 1)) * sd / math.sqrt(n)
                ref = {"n": n, "mean_diff": mean, "sd_diff": sd, "t_lo": mean - half, "t_hi": mean + half}
                for k, v in ref.items():
                    if abs(float(row[k]) - v) > 1e-8:
                        problems.append(f"{exp} contrasts {row['cell']} {m} {row['treatment']}-{row['control']} "
                                        f"{k}: file {row[k]} recomputed {v}")
                n_c += 1
        # summary.csv
        n_s = 0
        with open(edir / "summary.csv") as fh:
            for row in csv.DictReader(fh):
                vals = by[(row["cell"], row["arm"])]
                if int(row["n_runs"]) != len(vals):
                    problems.append(f"{exp} summary n_runs {row['cell']} {row['arm']}")
                for m in ("h_exp", "gini_exposure", "relevance", "miscalibration_kl", "user_control", "like_rate",
                          "delta_h_pref"):
                    xs = [v[m] for v in vals.values() if v[m] is not None]
                    if not xs:
                        continue
                    a = np.array(xs, dtype=float)
                    if abs(float(row[f"{m}_mean"]) - a.mean()) > TOL or abs(float(row[f"{m}_sd"]) - a.std(ddof=1)) > TOL:
                        problems.append(f"{exp} summary {row['cell']} {row['arm']} {m}")
                n_s += 1
        print(f"{exp}: contrasts recomputed {n_c}, summary rows recomputed {n_s}")
        verdict = json.loads((edir / "verdict.json").read_text())
        if exp == "EXP-003":
            for w in verdict["skew_interaction"]:
                blk = w["block"]

                def deltas(skew: str) -> np.ndarray:
                    k = f"{blk}:pool_skew={skew}"
                    s_, r_ = by[(k, "similarity")], by[(k, "random")]
                    return np.array([s_[s]["h_exp"] - r_[s]["h_exp"] for s in sorted(s_)], dtype=float)
                x, y = deltas("zipf"), deltas("uniform")
                vx, vy = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
                se = math.sqrt(vx + vy)
                df = (vx + vy) ** 2 / (vx ** 2 / (len(x) - 1) + vy ** 2 / (len(y) - 1))
                diff = float(x.mean() - y.mean())
                q = tq(df)
                for k, v in {"diff": diff, "se": se, "df": df, "lo": diff - q * se, "hi": diff + q * se}.items():
                    if abs(w[k] - v) > 1e-8:
                        problems.append(f"EXP-003 Welch {blk} {k}: file {w[k]} recomputed {v}")
                print(f"EXP-003 Welch {blk}: diff {diff:.6f} [{diff - q * se:.6f}, {diff + q * se:.6f}] df {df:.3f}")
        if exp == "EXP-002":
            for dfm in verdict["drift_form"]:
                k = f"driftform:alpha0={dfm['alpha0']}"
                s_, r_ = by[(k, "similarity")], by[(k, "random")]
                v = float(np.mean([s_[s]["delta_h_pref"] - r_[s]["delta_h_pref"] for s in sorted(s_)]))
                if abs(v - dfm["D_additive_clip"]) > TOL:
                    problems.append(f"EXP-002 drift form alpha0 {dfm['alpha0']}")
                print(f"EXP-002 drift form alpha0 {dfm['alpha0']}: D additive-clip recomputed {v:.6f}")
    return problems


# DOI suffixes such as 10.1145/3240323.3240372 are excluded by the "/" look-behind.
NUM = re.compile(r"(?<![\w./])-?\d[\d,]*\.\d{2,}(?![\d])")
EVIDENCE_GLOBS = ("research/experiments/EXP-00*/contrasts.csv", "research/experiments/EXP-00*/summary.csv",
                  "research/experiments/EXP-00*/verdict.json", "research/experiments/EXP-00*/tables.md",
                  "research/experiments/EXP-00*/run_manifest.json", "results/calibration/calibration.json",
                  "research/freeze.json", "research/experiment_journal.jsonl",
                  "results/exploratory/*/report/contrasts.csv", "results/exploratory/*/report/summary.csv",
                  "results/exploratory/m4-likerate-fit.json", "research/experiments/EXP-00*/runs.csv",
                  "results/derived/*.csv",
                  "research/protocol.md", "research/experiments/EXP-00*/protocol.md")
TARGETS = ("research/experiments/EXP-00*/report.md", "research/paper/manuscript.md",
           "research/paper/supplementary.md", "research/claims_register.csv")


def evidence_values(globs=EVIDENCE_GLOBS) -> set[str]:
    out: set[str] = set()
    for g in globs:
        for p in ROOT.glob(g):
            for tok in re.findall(r"-?\d+\.\d+(?:e-?\d+)?|-?\d+", p.read_text()):
                out.add(tok.lstrip("-"))  # exact token (full-precision constants)
                try:
                    v = float(tok)
                except ValueError:
                    continue
                for nd in range(1, 7):
                    out.add(f"{round(v, nd):.{nd}f}")
                    out.add(f"{round(abs(v), nd):.{nd}f}")
    return out


def part_b() -> dict[str, list[str]]:
    ev = evidence_values()
    unmatched: dict[str, list[str]] = {}
    for g in TARGETS:
        for p in sorted(ROOT.glob(g)):
            miss = []
            for tok in NUM.findall(p.read_text()):
                t = tok.replace(",", "").lstrip("-")
                nd = len(t.split(".")[1])
                if f"{float(t):.{nd}f}" not in ev:
                    miss.append(tok)
            unmatched[str(p.relative_to(ROOT))] = sorted(set(miss))
    return unmatched


SCOPED = {  # Part C: numbers in these sections must come from the named experiment's own outputs
    "5.1": ("EXP-001",), "5.2": ("EXP-002",), "5.3": ("EXP-003",), "5.4": ("EXP-004", "EXP-001"),
}


def part_c() -> tuple[dict[str, list[str]], list[str]]:
    """Section-scoped trace of manuscript results, and row-wise check of the derived tables."""
    text = (ROOT / "research/paper/manuscript.md").read_text()
    unmatched: dict[str, list[str]] = {}
    for sec, exps in SCOPED.items():
        body = text.split(f"### {sec} ")[1].split("\n### ")[0]
        ev = evidence_values(tuple(f"research/experiments/{e}/{f}" for e in exps
                                   for f in ("contrasts.csv", "summary.csv", "verdict.json", "tables.md")))
        miss = []
        for tok in NUM.findall(body):
            t = tok.replace(",", "").lstrip("-")
            if f"{float(t):.{len(t.split('.')[1])}f}" not in ev:
                miss.append(tok)
        unmatched[f"manuscript section {sec} vs {', '.join(exps)}"] = sorted(set(miss))
    rowerr: list[str] = []
    # Table S3 against results/derived/mmr_recovery.csv
    sup = (ROOT / "research/paper/supplementary.md").read_text()
    rec = list(csv.DictReader(open(ROOT / "results/derived/mmr_recovery.csv")))
    for r in rec:
        vals = (f"{float(r['similarity_minus_random']):.4f}", f"{float(r['mmr_minus_similarity']):.4f}",
                f"{float(r['recovery_share']):.3f}")
        line = f"| {vals[0]} | {vals[1]} | {vals[2]} |"
        if line not in sup:
            rowerr.append(f"Table S3 row missing or wrong: {r['exp_id']} {r['cell']} {vals}")
    # Table 7 against results/exploratory/m4-likerate-summary.csv
    lik = list(csv.DictReader(open(ROOT / "results/exploratory/m4-likerate-summary.csv")))
    for r in lik:
        m, lo, hi = (float(r[k]) for k in ("delta_mean", "t_lo", "t_hi"))
        cell = f"{'+' if m > 0 else ''}{m:.4f} [{lo:.4f}, {hi:.4f}]"
        if cell not in text:
            rowerr.append(f"Table 7 cell missing or wrong: {r['pool_skew']} midpoint {r['like_midpoint']} {cell}")
    return unmatched, rowerr


def part_d() -> list[str]:
    """Row-wise check of manuscript Tables 2 to 6 against contrasts.csv (exact formatted cells)."""
    s = (ROOT / "research/paper/manuscript.md").read_text()

    def con(e: str) -> dict:
        with open(ROOT / f"research/experiments/{e}/contrasts.csv") as fh:
            return {(r["cell"], r["metric"], r["treatment"], r["control"]): r for r in csv.DictReader(fh)}

    def ci(r: dict) -> str:
        return f"{float(r['mean_diff']):.4f} [{float(r['t_lo']):.4f}, {float(r['t_hi']):.4f}]"

    want = []
    c = con("EXP-001")
    for cell in ("main:alpha0=1.0,eta=0.0", "main:alpha0=0.1,eta=0.0", "main:alpha0=1.0,eta=0.2", "main:alpha0=0.1,eta=0.2"):
        r = c[(cell, "h_exp", "similarity", "random")]
        want.append(f"| {float(r['mean_diff']):.4f} | [{float(r['t_lo']):.4f}, {float(r['t_hi']):.4f}] | {float(r['d_z']):.2f} |")
    cell = "main:alpha0=1.0,eta=0.0"
    for t, k in (("popularity", "random"), ("similarity", "random"), ("bandit", "random"), ("mmr", "random"),
                 ("mmr", "similarity")):
        want.append(f"| {t} - {k} | {ci(c[(cell, 'h_exp', t, k)])} | "
                    f"{float(c[(cell, 'gini_exposure', t, k)]['mean_diff']):.4f} | ")
    c = con("EXP-002")
    for cell in ("main:alpha0=1.0,gamma=0.05", "main:alpha0=1.0,gamma=0.01", "main:alpha0=0.1,gamma=0.01",
                 "main:alpha0=0.1,gamma=0.05", "driftform:alpha0=1.0", "driftform:alpha0=0.1"):
        r = c[(cell, "delta_h_pref", "similarity", "random")]
        want.append(f"| {float(r['mean_diff']):.4f} | [{float(r['t_lo']):.4f}, {float(r['t_hi']):.4f}] |")
    c = con("EXP-003")
    for cell in ("tau0.1:pool_skew=zipf", "tau0.1:pool_skew=uniform", "tau0.3:pool_skew=uniform", "tau0.3:pool_skew=zipf"):
        want.append(f"| {ci(c[(cell, 'h_exp', 'similarity', 'random')])} | {ci(c[(cell, 'h_exp', 'mmr', 'similarity')])} |")
    c = con("EXP-004")
    for m in ("h_exp", "relevance", "miscalibration_kl", "like_rate"):
        want.append(" | ".join(ci(c[("main:base", m, t, k)]) for t, k in
                               (("similarity", "random"), ("mmr", "random"), ("mmr", "similarity"))))
    print(f"Part D: {len(want)} table rows checked")
    return [f"manuscript table row missing or wrong: {w}" for w in want if w not in s]


def main() -> int:
    print("== Part A: recomputation from raw outputs ==")
    probs = part_a()
    print(f"Part A problems: {len(probs)}")
    for p in probs:
        print("  " + p)
    print("== Part B: decimal numbers without a matching evidence value (manual review) ==")
    for f, miss in part_b().items():
        print(f"{f}: {len(miss)} unmatched" + (": " + ", ".join(miss) if miss else ""))
    print("== Part C: section-scoped manuscript trace and row-wise derived tables ==")
    sc, rowerr = part_c()
    for f, miss in sc.items():
        print(f"{f}: {len(miss)} unmatched" + (": " + ", ".join(miss) if miss else ""))
    print(f"row-wise errors: {len(rowerr)}")
    for e in rowerr:
        print("  " + e)
    derr = part_d()
    print(f"Part D errors: {len(derr)}")
    for e in derr:
        print("  " + e)
    return 1 if probs or rowerr or derr else 0


if __name__ == "__main__":
    raise SystemExit(main())
