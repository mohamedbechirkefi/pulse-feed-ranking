# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Build research/publication/artifact_manifest.json (master prompt 11.5) from committed records.

Every figure, table and claim used in the manuscript and reports is mapped to experiment id, run ids,
metric definition, result path (with SHA-256), generator script, config or protocol hash and code
revision. Claims are read from research/claims_register.csv; figures and tables are listed below.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_build_manifest.py
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = "f1838f3e8451c8c4275579a5736fe488354a8f3a"
XREV = "17c2e5f3cd1f905c7914f4bc4d5ed4c70811f4e3 (src/ identical to f1838f3; M4 scripts uncommitted at run time, committed in the M4 commit)"
CFG = {"EXP-001": "e51281119eed3c3bcd8ce8042cadc37b104c9b670d4992574e1d2b1095b7afcc",
       "EXP-002": "2c3b1816328f95d487bd83c1002a6db3970881a0eed91a2677569c3f2cfeed59",
       "EXP-003": "4aafb0446e763a37fe78cf83e00d94bdfc65fd5282579e82e5bd2cd1474b934f",
       "EXP-004": "43afda057c89f26add143561edbc0b0033de19675b8b5ef1626103518cdba9b2"}
PROT = {"EXP-001": "fbb70fc9d461e339f731ed3b928d024586d460a82543dec287edfbb7e7a38b20",
        "EXP-002": "e1f4d229803ee9684a12cb2c22ad5b217d8075d0f852ffc33f87604cb1b12b56",
        "EXP-003": "07e68a736cfa05850970859b0ac14e5c8a19e4ce241fe48940dcc83be3b672eb",
        "EXP-004": "dc004421d10eb9ff3b9b6f31b826de6db7863198db5e6b3784726f605b3bcb13"}
METRIC = {"h_exp": "H_exp(u) = -sum_z q_uz ln q_uz / ln K over the last W = 50 slates, position weights 0.85^(j-1); "
                   "run value = mean over users (protocol section 4)",
          "delta_h_pref": "(H(p_u(T)) - H(p_u(0))) / ln K, mean over users (EXP-002 protocol section 5)",
          "secondary": "Gini, relevance, miscalibration KL, user control, like rate (protocol section 5)"}
GEN = "scripts/analyse_experiment.py (verdict.json, contrasts.csv, summary.csv, figures); scripts/report_tables.py (tables.md)"


def sha(p: str) -> str:
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def conf_entry(aid: str, kind: str, exp: str, path: str, metric: str, runs: str, desc: str) -> dict:
    return {"artifact_id": aid, "kind": kind, "label": "confirmatory", "description": desc, "exp_id": exp,
            "run_ids": runs, "metric_definition": METRIC[metric], "result_path": path, "result_sha256": sha(path),
            "raw_results": f"results/raw/{exp}/runs/*.json (SHA-256 per file in research/experiments/{exp}/run_manifest.json)",
            "generator_script": GEN, "config_or_protocol_hash": {"config_canonical": CFG[exp], "protocol": PROT[exp]},
            "code_revision": REV}


def main() -> int:
    arts = []
    for exp, metric in (("EXP-001", "h_exp"), ("EXP-002", "delta_h_pref"), ("EXP-003", "h_exp"), ("EXP-004", "h_exp")):
        d = f"research/experiments/{exp}"
        for fig in sorted((ROOT / d / "figures").glob("*.svg")):
            rel = str(fig.relative_to(ROOT))
            m = "h_exp" if fig.stem.endswith("X01") and exp == "EXP-002" else metric
            arts.append(conf_entry(fig.stem, "figure", exp, rel, m, f"all runs of {exp}", "generated figure"))
        arts.append(conf_entry(f"{exp}-TABLES", "table", exp, f"{d}/tables.md", metric, f"all runs of {exp}",
                               "Tables A to E of the experiment report"))
        for f in ("verdict.json", "contrasts.csv", "summary.csv"):
            arts.append(conf_entry(f"{exp}-{f.split('.')[0].upper()}", "result", exp, f"{d}/{f}", metric,
                                   f"all runs of {exp}", f"analysis output {f}"))
    for aid, path, desc in (("FIG-M4-X01", "research/paper/figures/FIG-M4-X01.svg", "exploratory like-rate figure"),
                            ("XPL-M4-LIKERATE-SUMMARY", "results/exploratory/m4-likerate-summary.csv",
                             "exploratory like-rate summary table (manuscript Table 7)"),
                            ("XPL-M4-LIKERATE-FIT", "results/exploratory/m4-likerate-fit.json",
                             "midpoints fitted by the frozen calibration method for each target like rate")):
        arts.append({"artifact_id": aid, "kind": "figure" if aid.startswith("FIG") else "result",
                     "label": "exploratory", "description": desc, "exp_id": "XPL-M4-LIKERATE",
                     "run_ids": "XPL-M4-LIKERATE-{UNIFORM,ZIPF}-likerate-* (160 runs, seeds 960001 to 960005)",
                     "metric_definition": METRIC["h_exp"], "result_path": path, "result_sha256": sha(path),
                     "raw_results": "results/exploratory/m4-likerate-{uniform,zipf}/runs/*.json",
                     "generator_script": "scripts/m4_likerate_configs.py; pulse.cli run and report --no-pdf; "
                                         "scripts/m4_likerate_summary.py",
                     "config_or_protocol_hash": {
                         "uniform": "e10e8f06c5994110fd6ea420c7e9afad3bdf666ed6d19718dd23972ed3194a04",
                         "zipf": "0408cce6bff840bbe3c3df2a64db27ae949c4c85c26b0b88cb309a4d2d81c0ee"},
                     "code_revision": XREV})
    with open(ROOT / "research" / "claims_register.csv") as fh:
        for row in csv.DictReader(fh):
            arts.append({"artifact_id": row["claim_id"], "kind": "claim", "label": row["type"],
                         "description": row["text"], "exp_id": row["result_id"], "run_ids": row["run_ids"],
                         "metric_definition": METRIC["delta_h_pref"] if "preference entropy" in row["text"]
                         else METRIC["h_exp"] if "H_exp" in row["text"] else METRIC["secondary"],
                         "result_path": row["evidence_path"], "figure_or_table": row["figure_or_table"],
                         "manuscript_section": row["manuscript_section"], "generator_script": GEN,
                         "config_or_protocol_hash": row["config_hash"],
                         "code_revision": XREV if row["type"] == "exploratory result" else REV})
    out = {"schema_version": "1.0", "updated": "2026-11-25",
           "status": "M4 evidence audit: every manuscript and report number traced (research/publication/evidence_audit.md)",
           "fields_required_per_entry": ["artifact_id", "kind", "exp_id", "run_ids", "metric_definition", "result_path",
                                         "generator_script", "config_or_protocol_hash", "code_revision"],
           "artifacts": arts}
    p = ROOT / "research" / "publication" / "artifact_manifest.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(f"{p}: {len(arts)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
