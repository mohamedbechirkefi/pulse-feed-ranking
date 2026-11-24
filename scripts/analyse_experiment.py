# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Frozen analysis of one confirmatory experiment, from its raw result files.

Usage: PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-00N [RAW_DIR DEST_DIR]

Reads results/raw/EXP-00N (validated by the schema), runs the generic report generator
(pulse.report: per-run metrics, per-arm summary, all paired contrasts with Holm adjustment within
each cell and metric family, strip plots) and the frozen decision rules (pulse.analysis), then
writes into research/experiments/EXP-00N/: verdict.json, metrics.csv, summary.csv, contrasts.csv,
run_manifest.json (per-run provenance and raw-file SHA-256), runs.csv, config.json and figures/.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from pulse.analysis import ANALYSES, forest_svg, provenance, write_runs_csv
from pulse.manifest import REPO_ROOT
from pulse.report import generate
from pulse.schema import load_results


def _label(c: dict) -> str:
    cell = ",".join(f"{k}={v}" for k, v in c["cell"].items()) or "base"
    return f"{c['block']}:{cell} | {c['treatment']} - {c['control']}"


def _row(c: dict) -> dict:
    return {"label": _label(c), "mean": c["mean_diff"], "lo": c["t_lo"], "hi": c["t_hi"]}


def main(exp_id: str, raw: Path | None = None, dest: Path | None = None) -> int:
    """raw and dest default to the confirmatory locations; tests pass temporary directories."""
    raw = Path(raw) if raw else REPO_ROOT / "results" / "raw" / exp_id
    dest = Path(dest) if dest else REPO_ROOT / "research" / "experiments" / exp_id
    figs = dest / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    rep = generate(raw, pdf=False)
    for name in ("metrics.csv", "summary.csv", "contrasts.csv"):
        shutil.copy(rep["out"] / name, dest / name)
    for svg in sorted(rep["out"].glob("FIG-*.svg")):
        shutil.copy(svg, figs / f"{exp_id}-{svg.name}")
    results = load_results(raw)
    verdict = ANALYSES[exp_id](results)
    freeze = json.loads((REPO_ROOT / "research" / "freeze.json").read_text(encoding="utf-8"))
    dm = hashlib.sha256((REPO_ROOT / "data" / "manifest.json").read_bytes()).hexdigest()
    extra = {"data_manifest_frozen_sha256": freeze["sha256"]["data/manifest.json"]}
    if exp_id == "EXP-004":
        extra["heldout_preference_sha256_config"] = results[0]["config"]["user_pref_sha256"]
    prov = provenance(raw, dm, extra)
    (dest / "run_manifest.json").write_text(json.dumps(prov, indent=1) + "\n", encoding="utf-8")
    write_runs_csv(dest / "runs.csv", prov["runs"])
    shutil.copy(REPO_ROOT / "experiments" / f"{exp_id}.json", dest / "config.json")
    verdict["n_runs"] = prov["n_runs"]
    verdict["n_failed"] = prov["n_failed"]
    (dest / "verdict.json").write_text(json.dumps(verdict, indent=1, default=float) + "\n", encoding="utf-8")

    # Forest plot of the frozen contrasts (95% paired t-intervals; Welch for the EXP-003 interaction).
    if exp_id == "EXP-001":
        rows = [_row(verdict["primary"])] + [_row(c) for c in verdict["secondary_cells"]]
        xl = "H_exp(similarity) - H_exp(random), mean over 20 seeds with 95% t-interval"
    elif exp_id == "EXP-002":
        rows = [_row(verdict["primary"])] + [_row(c) for c in verdict["secondary_cells"]]
        rows += [_row(d["check"]) for d in verdict["drift_form"]]
        xl = "Delta H_pref(similarity) - Delta H_pref(random), mean over 20 seeds with 95% t-interval"
    elif exp_id == "EXP-003":
        rows = [_row(c) for c in verdict["cells"]] + [_row(c["mmr_minus_similarity"]) for c in verdict["cells"]]
        rows += [{"label": f"{i['block']} | interaction zipf - uniform (Welch)", "mean": i["diff"], "lo": i["lo"],
                  "hi": i["hi"]} for i in verdict["skew_interaction"]]
        xl = "difference in H_exp, mean over 20 seeds with 95% interval"
    else:
        rows = [_row(verdict["primary"])]
        xl = "H_exp(similarity) - H_exp(random), mean over 20 seeds with 95% t-interval"
    (figs / f"{exp_id}-FIG-C01.svg").write_text(
        forest_svg(rows, f"{exp_id}: frozen contrasts (confirmatory)", xl), encoding="utf-8")
    print(json.dumps({"experiment": exp_id, "n_runs": prov["n_runs"], "n_failed": prov["n_failed"],
                      "primary": {k: verdict["primary"][k] for k in
                                  ("mean_diff", "t_lo", "t_hi", "boot_lo", "boot_hi", "d_z", "reason")}},
                     indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:4]))
