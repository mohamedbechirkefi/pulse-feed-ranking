# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Result schema, run manifests, runner gate, failure recording, report generation, CLI."""
import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest

from pulse import cli
from pulse.config import ConfigError
from pulse.manifest import REPO_ROOT
from pulse.report import generate
from pulse.runner import ProtocolNotFrozen, execute, expand, load_experiment, protocol_frozen
from pulse.schema import SchemaError, load_result, validate_result

TINY = {"n_users": 5, "n_items": 60, "n_topics": 4, "pool_size": 10, "slate_size": 3, "n_steps": 6, "window": 3}


def tiny_exp(label="exploratory", out="results/exploratory/test"):
    return {"experiment_id": "XPL-TEST", "label": label, "output_dir": out, "base": dict(TINY),
            "seeds": {"first": 999001, "count": 3},
            "blocks": [{"name": "main", "factors": {"eta": [0.0, 0.2]},
                        "arms": [{"arm": "random", "ranker": "random"}, {"arm": "similarity", "ranker": "similarity"},
                                 {"arm": "mmr", "ranker": "mmr"}]}]}


def test_expand_counts_and_unique_ids():
    specs = expand(tiny_exp())
    assert len(specs) == 2 * 3 * 3 and len({s.run_id for s in specs}) == 18


@pytest.mark.parametrize("name,runs", [("EXP-001", 240), ("EXP-002", 240), ("EXP-003", 120)])
def test_registered_configs_expand_to_protocol_run_counts(name, runs):
    exp = load_experiment(REPO_ROOT / "experiments" / f"{name}.json")
    assert exp["label"] == "confirmatory" and len(expand(exp)) == runs


def test_end_to_end_run_and_report(tmp_path):
    out = execute(tiny_exp(), out_dir=tmp_path / "set")
    files = sorted((out / "runs").glob("*.json"))
    assert len(files) == 18
    r = load_result(files[0])
    assert r["label"] == "exploratory" and r["status"] == "ok"
    for key in ("config_hash", "seed", "git", "python", "numpy", "os", "cpu", "runtime_s", "peak_rss_bytes_process"):
        assert key in r["manifest"]
    assert r["manifest"]["config_hash"] == r["config_hash"]
    res = generate(out, pdf=False)
    rep = res["out"]
    for f in ("metrics.csv", "summary.csv", "contrasts.csv", "report.md", "FIG-X01.svg"):
        assert (rep / f).exists()
    rows = list(csv.DictReader((rep / "metrics.csv").open()))
    assert len(rows) == 18
    text = (rep / "report.md").read_text()
    assert "EXPLORATORY" in text
    # contrasts are paired by seed: 2 cells x (similarity, mmr vs random + mmr vs similarity) x metrics with values
    con = list(csv.DictReader((rep / "contrasts.csv").open()))
    h = [c for c in con if c["metric"] == "h_exp"]
    assert len(h) == 2 * 3 and all(c["n"] == "3" for c in h)


def test_reruns_are_identical(tmp_path):
    a = execute(tiny_exp(), out_dir=tmp_path / "a")
    b = execute(tiny_exp(), out_dir=tmp_path / "b")
    for fa in sorted((a / "runs").glob("*.json")):
        ra, rb = load_result(fa), load_result(b / "runs" / fa.name)
        assert ra["metrics"] == rb["metrics"] and ra["config_hash"] == rb["config_hash"]


def test_refuses_to_overwrite(tmp_path):
    execute(tiny_exp(), out_dir=tmp_path / "s")
    with pytest.raises(FileExistsError):
        execute(tiny_exp(), out_dir=tmp_path / "s")


def test_failed_runs_are_recorded_not_dropped(tmp_path):
    def boom(cfg, seed):
        if cfg.ranker == "mmr":
            raise FloatingPointError("injected failure")
        from pulse.simulate import simulate
        return simulate(cfg, seed)

    out = execute(tiny_exp(), out_dir=tmp_path / "f", simulate_fn=boom)
    recs = [load_result(f) for f in (out / "runs").glob("*.json")]
    failed = [r for r in recs if r["status"] == "failed"]
    assert len(recs) == 18 and len(failed) == 6 and "injected failure" in failed[0]["error"]
    man = json.loads((out / "set_manifest.json").read_text())
    assert man["n_failed"] == 6
    generate(out, pdf=False)  # the report must handle failed runs


def test_confirmatory_refused_while_protocol_unfrozen(tmp_path):
    ok, why = protocol_frozen("EXP-001")
    assert not ok and "DRAFT" in why
    exp = load_experiment(REPO_ROOT / "experiments" / "EXP-001.json")
    with pytest.raises(ProtocolNotFrozen):
        execute(exp, out_dir=tmp_path / "c")
    assert not (tmp_path / "c").exists()
    assert cli.main(["run", "--experiment", "EXP-001", "--out", str(tmp_path / "d")]) == 3


def fake_repo(tmp_path, status="frozen v1.0", draft=False, tamper=False):
    (tmp_path / "research" / "experiments" / "EXP-009").mkdir(parents=True)
    proto = tmp_path / "research" / "experiments" / "EXP-009" / "protocol.md"
    proto.write_text("protocol text\n")
    h = hashlib.sha256(proto.read_bytes()).hexdigest()
    if tamper:
        proto.write_text("protocol text, edited after freeze\n")
    (tmp_path / "research" / "protocol.md").write_text("Status: DRAFT\n" if draft else "Status: FROZEN v1.0\n")
    with (tmp_path / "research" / "experiment_registry.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["exp_id", "protocol_path", "protocol_hash", "status"])
        w.writerow(["EXP-009", "research/experiments/EXP-009/protocol.md", h, status])
    return tmp_path


def test_protocol_gate_logic(tmp_path):
    assert protocol_frozen("EXP-009", fake_repo(tmp_path / "a"))[0]
    assert not protocol_frozen("EXP-009", fake_repo(tmp_path / "b", draft=True))[0]
    assert not protocol_frozen("EXP-009", fake_repo(tmp_path / "c", tamper=True))[0]
    assert not protocol_frozen("EXP-009", fake_repo(tmp_path / "d", status="planned (protocol draft)"))[0]
    assert not protocol_frozen("EXP-404", fake_repo(tmp_path / "e"))[0]


def test_exploratory_output_location_enforced(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps(tiny_exp(out="results/raw/x")))
    with pytest.raises(ConfigError):
        load_experiment(p)
    p.write_text(json.dumps(tiny_exp(label="confirmatory", out="results/exploratory/x")))
    with pytest.raises(ConfigError):
        load_experiment(p)


def _good(tmp_path):
    out = execute(tiny_exp(), out_dir=tmp_path / "g")
    return load_result(next((out / "runs").glob("*.json")))


@pytest.mark.parametrize("mutate", [
    lambda r: r.pop("manifest"),
    lambda r: r.__setitem__("schema_version", "0.9"),
    lambda r: r.__setitem__("label", "final"),
    lambda r: r["metrics"].__setitem__("h_exp", 1.5),
    lambda r: r["metrics"].__setitem__("h_exp", float("nan")),
    lambda r: r["metrics"].__setitem__("h_exp", None),
    lambda r: r["metrics"].__setitem__("like_rate", "high"),
    lambda r: r["metrics"].pop("gini_exposure"),
    lambda r: r.__setitem__("config_hash", "abc"),
    lambda r: r.__setitem__("seed", -1),
    lambda r: r.__setitem__("error", "x"),
    lambda r: (r.__setitem__("status", "failed"), r.__setitem__("error", None)),
])
def test_schema_rejects_malformed(tmp_path, mutate):
    r = _good(tmp_path)
    validate_result(r)
    bad = copy.deepcopy(r)
    mutate(bad)
    with pytest.raises(SchemaError):
        validate_result(bad)


def test_cli_smoke_and_report_exploratory(tmp_path):
    assert cli.main(["smoke", "--out", str(tmp_path / "sm")]) == 0
    assert len(list((tmp_path / "sm" / "runs").glob("*.json"))) == 10
    assert cli.main(["report", "--results", str(tmp_path / "sm"), "--no-pdf"]) == 0
