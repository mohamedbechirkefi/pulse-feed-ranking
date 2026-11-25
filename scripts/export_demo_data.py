# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Export the published results for the M5 demo page (demo/public/data/results.json).

Reads committed files only: the analysis outputs of EXP-001 to EXP-004 (verdict.json, contrasts.csv,
EXP-001 tables.md and summary.csv), the committed exploratory summaries (XPL-M4-LIKERATE and the
pre-freeze seed-spread probe), the experiment registry, the claims register, the artifact manifest and
research/limitations.md. Nothing is recomputed: every value is copied, and every display string is
formatted exactly as the manuscript prints it (tests/test_demo_export.py checks this).

Output schema: lab-demo-results 1.0.0 (the shared demo template), with two project keys,
"exposure_heatmap" and "likerate_curve", validated by demo/src/results.ts. Deterministic: no
timestamps; sources are listed with their SHA-256.

Usage: .venv/bin/python scripts/export_demo_data.py [--check]
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"

EXP_DIR = "research/experiments"
LIKERATE = "results/exploratory/m4-likerate-summary.csv"
VARPROBE = "results/exploratory/var-probe/report/contrasts.csv"
REGISTRY = "research/experiment_registry.csv"
CLAIMS = "research/claims_register.csv"
MANIFEST = "research/publication/artifact_manifest.json"
LIMITATIONS = "research/limitations.md"

QUESTION = (
    "How do ranking objectives influence exposure diversity and simulated preference reinforcement "
    "when all rankers receive identical candidate pools?"
)
STATUS_LABEL = (
    "Simulation study. Confirmatory results for EXP-001 to EXP-004 hold at one calibrated like rate "
    "(0.577); an exploratory check bounds them; EXP-005 is registered, not frozen and not run. "
    "Manuscript version 0.2 is a preprint draft, not peer-reviewed; the owner's full-text review is pending (M6)."
)


class ExportError(RuntimeError):
    pass


def _read(rel: str) -> bytes:
    p = ROOT / rel
    if not p.exists():
        raise ExportError(f"missing input {rel}")
    return p.read_bytes()


def _csv(rel: str) -> list[dict[str, str]]:
    return list(csv.DictReader(_read(rel).decode("utf-8").splitlines()))


def f4(x: float, plus: bool = False) -> str:
    s = f"{x:.4f}"
    return ("+" + s) if plus and x > 0 else s


def interval(lo: float, hi: float, digits: int = 4) -> str:
    return f"[{lo:.{digits}f}, {hi:.{digits}f}]"


def contrast(rows: list[dict[str, str]], cell: str, metric: str, treat: str, ctrl: str) -> dict[str, float]:
    hit = [r for r in rows if (r["cell"], r["metric"], r["treatment"], r["control"]) == (cell, metric, treat, ctrl)]
    if len(hit) != 1:
        raise ExportError(f"expected one contrast row for {cell} {metric} {treat}-{ctrl}, found {len(hit)}")
    r = hit[0]
    return {"mean": float(r["mean_diff"]), "lo": float(r["t_lo"]), "hi": float(r["t_hi"]), "n": int(r["n"])}


def est(label: str, c: dict[str, float], unit: str, plus: bool = False, digits: int = 4) -> dict:
    disp = (f"{c['mean']:.{digits}f}" if digits != 4 else f4(c["mean"], plus))
    if plus and c["mean"] > 0 and not disp.startswith("+"):
        disp = "+" + disp
    return {
        "label": label,
        "estimate": c["mean"],
        "ci_low": c["lo"],
        "ci_high": c["hi"],
        "ci_level": 0.95,
        "unit": unit,
        "display": disp,
        "interval_display": interval(c["lo"], c["hi"], digits),
    }


H = "normalised entropy units"
D = "normalised entropy change"


def claims_for(claims: list[dict[str, str]], pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return [c["claim_id"] for c in claims if rx.search(c["result_id"]) or rx.search(c["run_ids"])]


def registry_row(reg: list[dict[str, str]], exp_id: str) -> dict[str, str]:
    hit = [r for r in reg if r["exp_id"] == exp_id]
    if len(hit) != 1:
        raise ExportError(f"{exp_id} not in the registry")
    return hit[0]


def verdict_text(v: dict) -> str:
    return "H1 supported" if v["h1_supported"] else f"H1 not supported ({v['reason']})"


def limitations() -> list[str]:
    out = []
    for line in _read(LIMITATIONS).decode("utf-8").splitlines():
        m = re.match(r"^\d+\. \*\*(.+?)\*\* (.+)$", line)
        if not m:
            continue
        title, body = m.group(1), m.group(2)
        first = re.split(r"(?<=[a-z0-9)])\. (?=[A-Z])", body, maxsplit=1)[0].rstrip(".") + "."
        out.append(f"{title} {first}")
    if not out:
        raise ExportError("no limitation items parsed")
    return out


def build() -> dict:
    reg = _csv(REGISTRY)
    claims = _csv(CLAIMS)
    manifest = json.loads(_read(MANIFEST))
    revs = {a.get("code_revision") for a in manifest["artifacts"] if a.get("label") == "confirmatory"}
    if len(revs) != 1:
        raise ExportError(f"confirmatory artifacts carry more than one code revision: {revs}")
    code_revision = revs.pop()

    sources = [REGISTRY, CLAIMS, MANIFEST, LIMITATIONS]
    experiments = []

    # EXP-001 ------------------------------------------------------------------------------
    v1 = json.loads(_read(f"{EXP_DIR}/EXP-001/verdict.json"))
    c1 = _csv(f"{EXP_DIR}/EXP-001/contrasts.csv")
    sources += [f"{EXP_DIR}/EXP-001/verdict.json", f"{EXP_DIR}/EXP-001/contrasts.csv"]
    cells1 = [("main:alpha0=1.0,eta=0.0", "eta 0.0, alpha_0 1.0 (primary)"),
              ("main:alpha0=0.1,eta=0.0", "eta 0.0, alpha_0 0.1"),
              ("main:alpha0=1.0,eta=0.2", "eta 0.2, alpha_0 1.0"),
              ("main:alpha0=0.1,eta=0.2", "eta 0.2, alpha_0 0.1")]
    e1 = [est(f"Similarity - random, H_exp, {lab}", contrast(c1, cell, "h_exp", "similarity", "random"), H)
          for cell, lab in cells1]
    pc = cells1[0][0]
    for t, c, lab in [("popularity", "random", "Popularity - random"), ("bandit", "random", "Bandit - random"),
                      ("mmr", "random", "MMR - random"), ("mmr", "similarity", "MMR - similarity")]:
        e1.append(est(f"{lab}, H_exp, primary cell", contrast(c1, pc, "h_exp", t, c), H))
    r1 = registry_row(reg, "EXP-001")
    cells_ok = all(x["h1_supported"] for x in v1["secondary_cells"])
    if not cells_ok:
        raise ExportError("EXP-001 secondary verdicts differ from the exported wording; update the exporter")
    experiments.append({
        "id": "EXP-001",
        "title": r1["title"],
        "status": f"confirmatory, complete ({v1['n_runs']} runs, {v1['n_failed']} failed)",
        "verdict": verdict_text(v1["primary"]) + (" in the primary cell and in all three secondary cells" if cells_ok else ""),
        "estimates": e1,
        "claim_ids": claims_for(claims, r"EXP-001|CONF-EXP-001"),
        "report_path": r1["report_path"],
        "notes": [
            "Paired by seed (common random numbers, 20 seeds per cell). The smallest effect of interest is 0.05.",
            "Popularity changed topic entropy by less than the smallest effect of interest: a practically null contrast, shown with the same weight as the others.",
        ],
    })

    # EXP-002 ------------------------------------------------------------------------------
    v2 = json.loads(_read(f"{EXP_DIR}/EXP-002/verdict.json"))
    c2 = _csv(f"{EXP_DIR}/EXP-002/contrasts.csv")
    sources += [f"{EXP_DIR}/EXP-002/verdict.json", f"{EXP_DIR}/EXP-002/contrasts.csv"]
    cells2 = [("main:alpha0=1.0,gamma=0.05", "gamma 0.05, alpha_0 1.0 (primary)"),
              ("main:alpha0=1.0,gamma=0.01", "gamma 0.01, alpha_0 1.0"),
              ("main:alpha0=0.1,gamma=0.01", "gamma 0.01, alpha_0 0.1"),
              ("main:alpha0=0.1,gamma=0.05", "gamma 0.05, alpha_0 0.1")]
    e2 = [est(f"Similarity - random, Delta H_pref, {lab}", contrast(c2, cell, "delta_h_pref", "similarity", "random"), D)
          for cell, lab in cells2]
    for a in ("1.0", "0.1"):
        e2.append(est(f"Drift-form check, additive-then-clip, alpha_0 {a}",
                      contrast(c2, f"driftform:alpha0={a}", "delta_h_pref", "similarity", "random"), D))
    dep = any(x["dependent_on_drift_form"] for x in v2["drift_form"])
    if not all(x["h1_supported"] for x in [v2["primary"], *v2["secondary_cells"]]):
        raise ExportError("EXP-002 cell verdicts differ from the exported wording; update the exporter")
    r2 = registry_row(reg, "EXP-002")
    experiments.append({
        "id": "EXP-002",
        "title": r2["title"],
        "status": f"confirmatory, complete ({v2['n_runs']} runs, {v2['n_failed']} failed)",
        "verdict": verdict_text(v2["primary"]) + " in all four cells; drift-form rule "
                   + ("met (dependent on the drift form)" if dep else "not met"),
        "estimates": e2,
        "claim_ids": claims_for(claims, r"EXP-002|CONF-EXP-002"),
        "report_path": r2["report_path"],
        "notes": [
            "Drift toward liked topics is an assumption of the model; it encodes reinforcement by construction and says nothing about whether people drift.",
            "The drift-form check is weak: it is close to a reparametrisation of gamma (limitations 12).",
        ],
    })

    # EXP-003 ------------------------------------------------------------------------------
    v3 = json.loads(_read(f"{EXP_DIR}/EXP-003/verdict.json"))
    c3 = _csv(f"{EXP_DIR}/EXP-003/contrasts.csv")
    sources += [f"{EXP_DIR}/EXP-003/verdict.json", f"{EXP_DIR}/EXP-003/contrasts.csv"]
    cells3 = [("tau0.1:pool_skew=zipf", "tau 0.1, Zipf (primary)"), ("tau0.1:pool_skew=uniform", "tau 0.1, uniform"),
              ("tau0.3:pool_skew=uniform", "tau 0.3, uniform"), ("tau0.3:pool_skew=zipf", "tau 0.3, Zipf")]
    e3 = [est(f"Similarity - random, H_exp, {lab}", contrast(c3, cell, "h_exp", "similarity", "random"), H)
          for cell, lab in cells3]
    e3 += [est(f"MMR - similarity, H_exp, {lab}", contrast(c3, cell, "h_exp", "mmr", "similarity"), H)
           for cell, lab in cells3]
    for w in v3["skew_interaction"]:
        tau = w["block"].replace("tau", "")
        e3.append(est(f"Interaction Zipf - uniform, tau {tau} (Welch)", {"mean": w["diff"], "lo": w["lo"], "hi": w["hi"]}, H))
    r3 = registry_row(reg, "EXP-003")
    crit = any(v3["skew_criterion_met"].values()) or any(v3["sharpness_criterion_met"].values())
    if not all(c["h1_supported"] for c in v3["cells"]) or any(c["contradiction"] for c in v3["cells"]):
        raise ExportError("EXP-003 cell verdicts differ from the exported wording; update the exporter")
    experiments.append({
        "id": "EXP-003",
        "title": r3["title"],
        "status": f"confirmatory sensitivity analysis, complete ({v3['n_runs']} runs, {v3['n_failed']} failed)",
        "verdict": "H1 supported in all four cells; invalidation criteria "
                   + ("met" if crit else "not met") + "; no sign reversal at the frozen calibration",
        "estimates": e3,
        "claim_ids": claims_for(claims, r"EXP-003|CONF-EXP-003"),
        "report_path": r3["report_path"],
        "notes": [
            "The Welch intervals compare two catalogs and are unpaired across skew levels.",
            "At lower like rates the Zipf contrast reverses sign (exploratory XPL-M4-LIKERATE below).",
        ],
    })

    # EXP-004 ------------------------------------------------------------------------------
    v4 = json.loads(_read(f"{EXP_DIR}/EXP-004/verdict.json"))
    c4 = _csv(f"{EXP_DIR}/EXP-004/contrasts.csv")
    sources += [f"{EXP_DIR}/EXP-004/verdict.json", f"{EXP_DIR}/EXP-004/contrasts.csv"]
    e4 = []
    for metric, mlab, unit in [("h_exp", "H_exp", H), ("relevance", "relevance", "mean true utility"),
                               ("miscalibration_kl", "miscalibration KL", "nats"), ("like_rate", "like rate", "share")]:
        for t, c, lab in [("similarity", "random", "Similarity - random"), ("mmr", "random", "MMR - random"),
                          ("mmr", "similarity", "MMR - similarity")]:
            e4.append(est(f"{lab}, {mlab}", contrast(c4, "main:base", metric, t, c), unit))
    r4 = registry_row(reg, "EXP-004")
    experiments.append({
        "id": "EXP-004",
        "title": r4["title"],
        "status": f"confirmatory second test, complete ({v4['n_runs']} runs, {v4['n_failed']} failed)",
        "verdict": verdict_text(v4["primary"]) + "; contradiction rule "
                   + ("met" if v4["primary"]["contradiction"] else "not met"),
        "estimates": e4,
        "claim_ids": claims_for(claims, r"EXP-004|CONF-EXP-004"),
        "report_path": r4["report_path"],
        "notes": [
            "Preferences are constructed from MovieLens 1M aggregates (held-out half); MovieLens users are not participants and no row-level data is shown or shipped.",
        ],
    })

    # XPL-M4-LIKERATE (exploratory, post hoc) ----------------------------------------------
    lr = _csv(LIKERATE)
    sources.append(LIKERATE)
    targets = ["0.02 (planning midpoint 0.5)", "0.05", "0.15", "0.30", "0.45", "0.577 (frozen calibration)", "0.70", "0.85"]
    by_cat: dict[str, list[dict[str, str]]] = {"uniform": [], "zipf": []}
    for row in lr:
        by_cat[row["pool_skew"]].append(row)
    if any(len(v) != len(targets) for v in by_cat.values()):
        raise ExportError("m4-likerate-summary.csv does not have eight levels per catalog")
    e5, curve = [], []
    for cat, catlab in (("uniform", "uniform catalog"), ("zipf", "Zipf catalog")):
        rows = sorted(by_cat[cat], key=lambda r: float(r["fitted_target_true_like_rate_uniform_world"]))
        for row, tlab in zip(rows, targets):
            c = {"mean": float(row["delta_mean"]), "lo": float(row["t_lo"]), "hi": float(row["t_hi"])}
            x = est(f"Similarity - random, H_exp, like rate {tlab}, {catlab}", c, H, plus=True)
            e5.append(x)
            curve.append({
                "catalog": cat,
                "target_like_rate": float(row["fitted_target_true_like_rate_uniform_world"]),
                "target_label": tlab,
                "n_seeds": int(row["n_seeds"]),
                "estimate": c["mean"], "ci_low": c["lo"], "ci_high": c["hi"],
                "display": x["display"], "interval_display": x["interval_display"],
            })
    experiments.append({
        "id": "XPL-M4-LIKERATE",
        "title": "Exploratory check: dependence of the primary contrast on the like rate",
        "status": "exploratory, post hoc (designed after the confirmatory results; 5 seeds per cell; 160 runs, 0 failed)",
        "verdict": "no frozen rule applies; it never changes a confirmatory verdict",
        "estimates": e5,
        "claim_ids": claims_for(claims, r"XPL-M4-LIKERATE"),
        "report_path": "research/paper/manuscript.md section 5.5; results/exploratory/m4-likerate-summary.csv",
        "notes": [
            "Settings of the EXP-003 tau 0.1 block (static preferences, eta 0.1, alpha_0 1.0); seeds disjoint from the confirmatory seeds.",
            "Under the uniform catalog the effect is below the smallest effect of interest at low like rates; under the Zipf catalog its sign reverses there.",
        ],
    })

    # Pre-freeze seed-spread probe (exploratory disclosure) --------------------------------
    vp = contrast(_csv(VARPROBE), "main:base", "h_exp", "similarity", "random")
    sources.append(VARPROBE)
    experiments.append({
        "id": "XPL-VAR-PROBE",
        "title": "Pre-freeze exploratory probe at the planning midpoint",
        "status": f"exploratory, before the freeze (planning midpoint 0.5; {vp['n']} seeds; earlier code state)",
        "verdict": "no frozen rule applies; a near-zero contrast, disclosed because the recalibration was approved with it in view",
        "estimates": [est("Similarity - random, H_exp, EXP-001 primary cell settings", vp, H, digits=6)],
        "claim_ids": claims_for(claims, r"var-probe"),
        "report_path": "results/exploratory/var-probe/report/report.md; research/paper/manuscript.md section 4.6",
        "notes": ["Not comparable as a test: different calibration and code state."],
    })

    # EXP-005 (registered, not frozen, not run) --------------------------------------------
    r5 = registry_row(reg, "EXP-005")
    if r5["protocol_hash"]:
        raise ExportError("EXP-005 has a protocol hash: its status must be re-read before export")
    experiments.append({
        "id": "EXP-005",
        "title": r5["title"],
        "status": "registered, not frozen, not run",
        "verdict": "none: no data exists; the protocol waits for the owner's freeze decision",
        "estimates": [],
        "claim_ids": claims_for(claims, r"EXP-005"),
        "report_path": "none (not run); protocol draft research/experiments/EXP-005/protocol.md",
        "notes": ["Six design parameters are open for the owner at freeze. No result of EXP-005 is shown anywhere on this page."],
    })

    # Measured exposure heatmap: EXP-001 per-arm H_exp (mean and SD over 20 seeds) ------------
    summ = _csv(f"{EXP_DIR}/EXP-001/summary.csv")
    tables = f"{EXP_DIR}/EXP-001/tables.md"
    sources += [f"{EXP_DIR}/EXP-001/summary.csv", tables]
    arms = [("random", "Random"), ("popularity", "Popularity"), ("bandit", "Bandit (LinUCB)"),
            ("mmr", "MMR"), ("similarity", "Similarity")]
    values = []
    for cell, lab in cells1:
        for arm, _ in arms:
            hit = [r for r in summ if r["cell"] == cell and r["arm"] == arm]
            if len(hit) != 1:
                raise ExportError(f"summary row missing for {cell} {arm}")
            m, s = float(hit[0]["h_exp_mean"]), float(hit[0]["h_exp_sd"])
            values.append({"arm": arm, "cell": cell, "mean": m, "sd": s, "n": int(hit[0]["n_ok"]),
                           "display": f"{m:.4f} ({s:.4f})"})
    heatmap = {
        "experiment_id": "EXP-001",
        "label": "measured, confirmatory",
        "metric": "H_exp, final-window normalised exposure topic entropy (0 = one topic, 1 = all ten topics equally)",
        "uncertainty": "SD over 20 seeds in parentheses",
        "source": tables,
        "arms": [{"id": a, "label": l} for a, l in arms],
        "cells": [{"id": c, "label": l} for c, l in cells1],
        "values": values,
    }

    likerate_curve = {
        "experiment_id": "XPL-M4-LIKERATE",
        "label": "measured, exploratory",
        "metric": "similarity minus random in H_exp, mean paired difference",
        "uncertainty": "95% paired t-interval over 5 seeds",
        "sesoi": 0.05,
        "frozen_like_rate": 0.577,
        "points": curve,
    }

    assumptions = [
        {"name": "Topics, items, users", "value": "K = 10 topics, N = 1,000 items, U = 200 simulated users per run", "source": "protocol v1.0, manuscript section 3"},
        {"name": "Loop", "value": "T = 200 steps; candidate pool C = 50, identical across rankers; slate k = 10", "source": "manuscript section 3"},
        {"name": "Examination", "value": "position j examined with probability 0.85^(j-1)", "source": "manuscript section 3"},
        {"name": "Choice", "value": "like with probability sigmoid((r_ui - c) / tau); feedback flipped with probability eta", "source": "manuscript section 3"},
        {"name": "Calibrated like rate", "value": "L* = 0.577143, the share of MovieLens 1M calibration-half ratings of 4 or more (a selected-exposure like rate)", "source": "manuscript section 4.3"},
        {"name": "Fitted midpoints", "value": "c = 0.066421 for tau 0.1 and 0.005990 for tau 0.3; c_ML = 0.061067", "source": "manuscript section 4.3"},
        {"name": "Drift (EXP-002 only)", "value": "after each like of topic z: p_u <- normalise((1 - gamma) p_u + gamma onehot(z))", "source": "manuscript section 3"},
        {"name": "Smallest effect of interest", "value": "0.05 normalised entropy units", "source": "frozen decision rule, manuscript section 4.4"},
    ]

    hashed = [{"path": p, "sha256": hashlib.sha256(_read(p)).hexdigest()} for p in sources]
    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "PULSE",
        "question": QUESTION,
        "status_label": STATUS_LABEL,
        "code_revision": code_revision,
        "sources": hashed,
        "experiments": experiments,
        "assumptions": assumptions,
        "limitations": limitations(),
        "exposure_heatmap": heatmap,
        "likerate_curve": likerate_curve,
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("EXPORT-CHECK " + ("identical" if same else "DIFFERS"))
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
