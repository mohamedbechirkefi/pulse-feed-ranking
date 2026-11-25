# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo shows exactly the numbers of the manuscript.

1. Re-running the export in memory reproduces the committed demo/public/data/results.json byte for byte.
2. Every display and interval_display string appears verbatim in research/paper/manuscript.md, and each
   estimate's pair appears on one manuscript line. Documented exception: the exposure heatmap prints
   per-arm means with SDs ("0.9932 (0.0009)"), which the manuscript does not tabulate; those strings must
   appear verbatim in the experiment's committed report table (research/experiments/EXP-001/tables.md).
3. The sandbox parity fixture is reproduced by the Python engine (scripts/export_sandbox_fixture.py).
4. EXP-005 is shown as registered, not run, with no estimate.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = (ROOT / "research/paper/manuscript.md").read_text(encoding="utf-8")
COMMITTED = ROOT / "demo/public/data/results.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def export():
    return _load("export_demo_data")


@pytest.fixture(scope="module")
def data():
    return json.loads(COMMITTED.read_text(encoding="utf-8"))


def test_committed_export_is_reproduced(export):
    assert COMMITTED.read_text(encoding="utf-8") == export.render(export.build())


def test_schema_and_no_timestamp(data):
    assert data["schema"] == "lab-demo-results" and data["schema_version"] == "1.0.0"
    text = COMMITTED.read_text(encoding="utf-8")
    assert "2026-" not in text and "T00:" not in text


def test_source_hashes_match_files(data):
    assert data["sources"]
    for s in data["sources"]:
        assert hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest() == s["sha256"], s["path"]


def test_every_display_string_is_printed_in_the_manuscript(data):
    lines = MANUSCRIPT.splitlines()
    n = 0
    for e in data["experiments"]:
        for x in e["estimates"]:
            d, i = x["display"], x["interval_display"]
            assert d in MANUSCRIPT, (e["id"], x["label"], d)
            assert i in MANUSCRIPT, (e["id"], x["label"], i)
            assert any(d in ln and i in ln for ln in lines), (e["id"], x["label"], d, i)
            n += 1
    for p in data["likerate_curve"]["points"]:
        assert any(p["display"] in ln and p["interval_display"] in ln for ln in lines), p
    assert n >= 50


def test_display_strings_match_the_numbers(data):
    for e in data["experiments"]:
        for x in e["estimates"]:
            digits = len(x["display"].split(".")[1])
            assert float(x["display"]) == pytest.approx(round(x["estimate"], digits), abs=10 ** -digits / 2)
            lo, hi = (float(v) for v in x["interval_display"].strip("[]").split(", "))
            assert lo == pytest.approx(x["ci_low"], abs=10 ** -digits) and hi == pytest.approx(x["ci_high"], abs=10 ** -digits)


def test_heatmap_exception_is_in_the_report_table(data):
    h = data["exposure_heatmap"]
    table = (ROOT / h["source"]).read_text(encoding="utf-8")
    assert h["source"] == "research/experiments/EXP-001/tables.md"
    for v in h["values"]:
        assert f"| {v['cell']} | {v['arm']} | " in table
        assert v["display"] in table, v
    # The two values the manuscript prints are also verbatim there.
    means = {(v["cell"], v["arm"]): v["display"].split(" ")[0] for v in h["values"]}
    for key in [("main:alpha0=1.0,eta=0.0", "random"), ("main:alpha0=1.0,eta=0.0", "similarity")]:
        assert means[key] in MANUSCRIPT


def test_status_labels_and_exp005(data):
    by = {e["id"]: e for e in data["experiments"]}
    assert set(by) >= {"EXP-001", "EXP-002", "EXP-003", "EXP-004", "EXP-005", "XPL-M4-LIKERATE"}
    assert by["EXP-005"]["status"] == "registered, not frozen, not run"
    assert by["EXP-005"]["estimates"] == []
    for k in ("EXP-001", "EXP-002", "EXP-003", "EXP-004"):
        assert by[k]["status"].startswith("confirmatory")
        assert "H1 supported" in by[k]["verdict"]
    assert by["XPL-M4-LIKERATE"]["status"].startswith("exploratory")
    assert "invalidation criteria not met" in by["EXP-003"]["verdict"]


def test_sandbox_fixture_is_reproduced():
    fx = _load("export_sandbox_fixture")
    assert fx.OUT.read_text(encoding="utf-8") == fx.render(fx.build())
