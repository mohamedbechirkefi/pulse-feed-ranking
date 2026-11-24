# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Report generator: tables, figures and a PDF built only from validated result files.

Outputs, written into <results>/report/: metrics.csv (one row per run), summary.csv
(per block, cell and arm), contrasts.csv (paired by seed), FIG-*.svg, report.md and
report.pdf (pandoc to Typst, compiled by the typst Python package; D-002).
"""
from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

from .schema import METRICS, load_results
from .stats import holm, paired_summary

from .manifest import REPO_ROOT

# Shared zero-cost toolchain next to the repository (D-002); overridable by environment variables.
PANDOC = Path(os.environ.get("PULSE_PANDOC", REPO_ROOT.parent / ".tools" / "pandoc"))
TYPST_PY = Path(os.environ.get("PULSE_TYPST_PYTHON", REPO_ROOT.parent / ".tools" / "py" / "bin" / "python"))
CONTROL = "random"
EXTRA_CONTRASTS = (("mmr", "similarity"),)


def _cell_key(r: dict) -> str:
    return r["block"] + ":" + (",".join(f"{k}={v}" for k, v in r["cell"].items()) or "base")


def _fmt(v, nd: int = 4) -> str:
    if v is None:
        return "NA"
    if isinstance(v, float):
        if math.isnan(v):
            return "NA"
        return f"{v:.{nd}f}"
    return str(v)


def metric_rows(results: list[dict]) -> list[dict]:
    rows = []
    for r in results:
        row = {"run_id": r["run_id"], "label": r["label"], "block": r["block"], "cell": _cell_key(r),
               "arm": r["arm"], "seed": r["seed"], "status": r["status"], "config_hash": r["config_hash"],
               "runtime_s": r["manifest"]["runtime_s"]}
        for m in METRICS:
            row[m] = r["metrics"].get(m)
        rows.append(row)
    return rows


def summarise(results: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in results:
        groups[(_cell_key(r), r["arm"])].append(r)
    out = []
    for (cell, arm), rs in sorted(groups.items()):
        ok = [r for r in rs if r["status"] == "ok"]
        row = {"cell": cell, "arm": arm, "n_runs": len(rs), "n_ok": len(ok)}
        for m in METRICS:
            vals = [r["metrics"][m] for r in ok if r["metrics"][m] is not None]
            row[f"{m}_mean"] = float(np.mean(vals)) if vals else None
            row[f"{m}_sd"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else None
        out.append(row)
    return out


def contrasts(results: list[dict]) -> list[dict]:
    """Paired-by-seed contrasts within each cell: every arm minus random, plus MMR minus similarity."""
    by_cell: dict[str, dict[str, dict[int, dict]]] = defaultdict(lambda: defaultdict(dict))
    for r in results:
        if r["status"] == "ok":
            by_cell[_cell_key(r)][r["arm"]][r["seed"]] = r
    out = []
    for cell, arms in sorted(by_cell.items()):
        pairs = [(a, CONTROL) for a in sorted(arms) if a != CONTROL and CONTROL in arms]
        pairs += [(a, b) for a, b in EXTRA_CONTRASTS if a in arms and b in arms]
        for m in METRICS:
            fam = []
            for a, b in pairs:
                seeds = sorted(set(arms[a]) & set(arms[b]))
                xa = [arms[a][s]["metrics"][m] for s in seeds]
                xb = [arms[b][s]["metrics"][m] for s in seeds]
                if not seeds or any(v is None for v in xa + xb):
                    continue
                ps = paired_summary(xa, xb)
                fam.append({"cell": cell, "metric": m, "treatment": a, "control": b, **ps.to_dict()})
            adj = holm([f["p_two_sided"] for f in fam])
            for f, p in zip(fam, adj):
                f["p_holm"] = p
            out.extend(fam)
    return out


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0])
    for r in rows[1:]:
        keys += [k for k in r if k not in keys]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})


def strip_plot_svg(results: list[dict], metric: str, title: str) -> str:
    """Per-seed values of one metric, one row per (cell, arm); no external plotting library."""
    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in results:
        if r["status"] == "ok" and r["metrics"].get(metric) is not None:
            groups[(_cell_key(r), r["arm"])].append(r["metrics"][metric])
    keys = sorted(groups)
    if not keys:
        raise ValueError(f"no values for {metric}")
    vals = [v for k in keys for v in groups[k]]
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        lo, hi = lo - 0.01, hi + 0.01
    pad = 0.05 * (hi - lo)
    lo, hi = lo - pad, hi + pad
    left, right, top, rowh = 330, 40, 50, 18
    width = 900
    height = top + rowh * len(keys) + 50
    plot_w = width - left - right

    def x(v: float) -> float:
        return left + (v - lo) / (hi - lo) * plot_w

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif" font-size="11">',
             f'<rect width="{width}" height="{height}" fill="white"/>',
             f'<text x="{left}" y="22" font-size="13" font-weight="bold">{title}</text>']
    for i in range(6):
        v = lo + i * (hi - lo) / 5
        parts.append(f'<line x1="{x(v):.1f}" y1="{top - 6}" x2="{x(v):.1f}" y2="{top + rowh * len(keys)}" stroke="#ddd"/>')
        parts.append(f'<text x="{x(v):.1f}" y="{top + rowh * len(keys) + 16}" text-anchor="middle">{v:.3f}</text>')
    parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 10}" text-anchor="middle">{metric} (per seed; bar = mean)</text>')
    for j, k in enumerate(keys):
        y = top + rowh * j + rowh / 2
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{k[0]} | {k[1]}</text>')
        for v in groups[k]:
            parts.append(f'<circle cx="{x(v):.1f}" cy="{y:.1f}" r="3" fill="#1f5f8b" fill-opacity="0.6"/>')
        mu = float(np.mean(groups[k]))
        parts.append(f'<line x1="{x(mu):.1f}" y1="{y - 6:.1f}" x2="{x(mu):.1f}" y2="{y + 6:.1f}" stroke="#b33" stroke-width="2"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _md_table(rows: list[dict], cols: list[str]) -> str:
    head = "| " + " | ".join(cols) + " |\n| " + " | ".join("---" for _ in cols) + " |\n"
    return head + "".join("| " + " | ".join(_fmt(r.get(c)) for c in cols) + " |\n" for r in rows)


def build_markdown(results: list[dict], summary: list[dict], contr: list[dict], set_manifest: dict,
                   figures: list[tuple[str, str]]) -> str:
    label = {r["label"] for r in results}
    banner = ("**EXPLORATORY. Not a finding. Protocol not frozen; these runs inform planning values only.**"
              if label == {"exploratory"} else f"Label: {sorted(label)}")
    runtimes = [r["manifest"]["runtime_s"] for r in results]
    failed = [r for r in results if r["status"] != "ok"]
    lines = [
        "<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->",
        f"# {set_manifest['experiment_id']} result set report (generated)",
        "",
        banner,
        "",
        f"Generated by `pulse.report` from {len(results)} validated result files. "
        f"Git revision at run time: {results[0]['manifest']['git']['commit']} "
        f"(dirty: {results[0]['manifest']['git']['dirty']}). Experiment config hash: {set_manifest['experiment_config_hash']}.",
        "",
        "## Execution",
        "",
        f"- Runs: {len(results)}; failed: {len(failed)}.",
        f"- Wall clock for the set: {set_manifest['wall_clock_s']} s.",
        f"- Runtime per run: mean {np.mean(runtimes):.3f} s, min {np.min(runtimes):.3f} s, max {np.max(runtimes):.3f} s.",
        f"- Platform: {results[0]['manifest']['os']}; CPU: {results[0]['manifest']['cpu']}; "
        f"Python {results[0]['manifest']['python']}; numpy {results[0]['manifest']['numpy']}.",
        "",
    ]
    if failed:
        lines += ["Failed runs:", ""] + [f"- {r['run_id']}: {r['error'].splitlines()[0]}" for r in failed] + [""]
    short = [{"cell": r["cell"], "arm": r["arm"], "n": r["n_ok"], "H_exp": r["h_exp_mean"], "H_exp SD": r["h_exp_sd"],
              "Gini": r["gini_exposure_mean"], "rel.": r["relevance_mean"], "like": r["like_rate_mean"],
              "ctrl": r["user_control_mean"], "dH_pref": r["delta_h_pref_mean"]} for r in summary]
    lines += ["## Per-arm summary (mean over seeds)", "",
              "H_exp: final-window normalised exposure topic entropy; Gini: item exposure concentration; rel.: mean "
              "true utility of examined items; like: observed like rate; ctrl: user-control metric; dH_pref: "
              "normalised preference-entropy change (drifting model only).", "",
              _md_table(short, list(short[0])), ""]
    prim = [{"cell": c["cell"], "metric": c["metric"], "contrast": f"{c['treatment']} - {c['control']}", "n": c["n"],
             "mean": c["mean_diff"], "SD": c["sd_diff"],
             "95% t CI": f"[{_fmt(c['t_lo'])}, {_fmt(c['t_hi'])}]",
             "95% boot CI": f"[{_fmt(c['boot_lo'])}, {_fmt(c['boot_hi'])}]",
             "d_z": c["d_z"], "p Holm": c["p_holm"]}
            for c in contr if c["metric"] in ("h_exp", "delta_h_pref")]
    lines += ["## Paired contrasts (treatment minus control, paired by seed)", "",
              "95% t-interval and percentile bootstrap (10,000 resamples) over seeds; d_z = mean / SD of differences; "
              "Holm adjustment within each cell and metric family. All metrics are in contrasts.csv. With few seeds "
              "these intervals are wide and only indicate scale.", ""]
    if prim:
        lines += [_md_table(prim, list(prim[0])), ""]
    for fig_id, caption in figures:
        lines += [f"![{fig_id}. {caption}]({fig_id}.svg)", ""]
    return "\n".join(lines)


def build_pdf(md_path: Path) -> Path | None:
    """Markdown to Typst with pandoc, compiled by the typst Python package. Returns the PDF path."""
    if not PANDOC.exists() or not TYPST_PY.exists():
        return None
    typ = md_path.with_suffix(".typ")
    subprocess.run([str(PANDOC), md_path.name, "-s", "-t", "typst", "-V", "mainfont=Libertinus Serif", "-V", "fontsize=9pt", "-V", "papersize=a4",
                    "-o", typ.name], cwd=md_path.parent, check=True)
    pdf = md_path.with_suffix(".pdf")
    subprocess.run([str(TYPST_PY), "-I", "-c",
                    "import sys, typst; typst.compile(sys.argv[1], output=sys.argv[2], root=sys.argv[3])",
                    str(typ), str(pdf), str(md_path.parent)], check=True)
    return pdf


def generate(results_dir: Path, pdf: bool = True) -> dict:
    results_dir = Path(results_dir)
    results = load_results(results_dir)
    set_manifest = json.loads((results_dir / "set_manifest.json").read_text(encoding="utf-8"))
    out = results_dir / "report"
    if out.exists():
        shutil.rmtree(out)  # derived files only; regenerated from the raw run files
    out.mkdir(parents=True)
    rows = metric_rows(results)
    summary = summarise(results)
    contr = contrasts(results)
    _write_csv(out / "metrics.csv", rows)
    _write_csv(out / "summary.csv", summary)
    _write_csv(out / "contrasts.csv", contr)
    figures = []
    for fig_id, metric in (("FIG-X01", "h_exp"), ("FIG-X02", "delta_h_pref")):
        if any(r["status"] == "ok" and r["metrics"].get(metric) is not None for r in results):
            title = f"{metric} per seed, by cell and arm ({set_manifest['label']})"
            (out / f"{fig_id}.svg").write_text(strip_plot_svg(results, metric, title), encoding="utf-8")
            figures.append((fig_id, f"{metric} for every run (dots, one per seed) and its mean (bar), "
                                    f"by cell and arm. Unitless. Label: {set_manifest['label']}."))
    md = build_markdown(results, summary, contr, set_manifest, figures)
    (out / "report.md").write_text(md, encoding="utf-8")
    pdf_path = build_pdf(out / "report.md") if pdf else None
    return {"out": out, "n_runs": len(results), "pdf": pdf_path, "summary": summary, "contrasts": contr}
