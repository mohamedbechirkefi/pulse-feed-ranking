# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Frozen decision rules and analysis helpers (written before any confirmatory output)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from pulse.analysis import (analyse_exp002, analyse_exp003, analyse_exp004, contrast, forest_svg,
                            primary_verdict, welch_interval)
from pulse.stats import t_cdf, t_ppf


@pytest.mark.parametrize("mean,lo,hi,supported,reason", [
    (-0.10, -0.12, -0.08, True, "H1 supported"),
    (-0.05, -0.06, -0.04, True, "H1 supported"),           # boundary: estimate equal to -SESOI
    (-0.03, -0.04, -0.02, False, "no practically relevant reduction"),
    (-0.10, -0.20, 0.00, False, "interval includes 0"),     # upper bound >= 0 is a contradiction
    (0.01, -0.01, 0.03, False, "interval includes 0"),
    (0.08, 0.05, 0.11, False, "sign reversal"),
])
def test_primary_verdict(mean, lo, hi, supported, reason):
    v = primary_verdict(mean, lo, hi)
    assert v["h1_supported"] is supported
    assert v["contradiction"] is (not supported)
    assert v["reason"] == reason


def test_welch_interval_golden():
    x, y = [1, 2, 3, 4], [2, 4, 6, 8, 10]
    w = welch_interval(x, y)
    va, vb = (5 / 3) / 4, 10 / 5
    assert w["diff"] == pytest.approx(-3.5)
    assert w["se"] == pytest.approx(math.sqrt(va + vb))
    assert w["df"] == pytest.approx((va + vb) ** 2 / (va ** 2 / 3 + vb ** 2 / 4))
    # the half-width is the 0.975 quantile of t with the fractional Welch df
    assert t_cdf((w["hi"] - w["diff"]) / w["se"], w["df"]) == pytest.approx(0.975, abs=1e-9)
    assert w["lo"] < w["diff"] < w["hi"]


def test_t_ppf_accepts_fractional_df_and_is_monotone():
    assert t_ppf(0.975, 5.0) == pytest.approx(2.5706, abs=1e-4)
    assert t_ppf(0.975, 6.0) < t_ppf(0.975, 5.5) < t_ppf(0.975, 5.0)


def test_welch_needs_two_values():
    with pytest.raises(ValueError):
        welch_interval([1.0], [1.0, 2.0])


def _rec(block, cell, arm, seed, **metrics):
    base = {m: 0.5 for m in ("h_exp", "delta_h_pref")}
    base.update(metrics)
    return {"block": block, "cell": cell, "arm": arm, "seed": seed, "status": "ok", "metrics": base}


def test_contrast_pairs_by_seed_and_ignores_failed_runs():
    rs = [_rec("main", {}, "random", s, h_exp=0.9) for s in range(5)]
    rs += [_rec("main", {}, "similarity", s, h_exp=0.8 + 0.001 * s) for s in range(5)]
    rs.append({**_rec("main", {}, "similarity", 99, h_exp=0.1), "status": "failed"})
    c = contrast(rs, "main", {}, "similarity", "random", "h_exp")
    assert c["seeds"] == [0, 1, 2, 3, 4]
    assert c["mean_diff"] == pytest.approx(-0.098)


def test_exp004_sign_reversal_flag():
    rng = np.random.default_rng(0)
    rs = [_rec("main", {}, "random", s, h_exp=0.80) for s in range(20)]
    rs += [_rec("main", {}, "similarity", s, h_exp=0.90 + 0.001 * rng.standard_normal()) for s in range(20)]
    v = analyse_exp004(rs)["primary"]
    assert v["reason"] == "sign reversal" and v["sign_reversal_rule_15_9_applies"]


def test_exp003_criteria_and_interaction():
    rs = []
    for block in ("tau0.1", "tau0.3"):
        for skew, gap in (("uniform", -0.2), ("zipf", 0.1)):
            for s in range(20):
                jitter = 0.001 * ((s * 7) % 5)
                rs.append(_rec(block, {"pool_skew": skew}, "random", s, h_exp=0.9))
                rs.append(_rec(block, {"pool_skew": skew}, "similarity", s, h_exp=0.9 + gap + jitter))
                rs.append(_rec(block, {"pool_skew": skew}, "mmr", s, h_exp=0.95))
    v = analyse_exp003(rs)
    assert v["restricted_to_balanced_pools"] is True
    assert v["skew_criterion_met"] == {"tau0.1": True, "tau0.3": True}
    assert v["sharpness_criterion_met"] == {"uniform": False, "zipf": True}
    assert v["primary"]["sign_reversal_rule_15_9_applies"] is True
    for i in v["skew_interaction"]:
        assert i["diff"] == pytest.approx(0.3)


def test_exp002_drift_form_dependence():
    rs = []
    for a0 in (1.0, 0.1):
        for g in (0.01, 0.05):
            for s in range(10):
                rs.append(_rec("main", {"gamma": g, "alpha0": a0}, "random", s, delta_h_pref=-0.1))
                rs.append(_rec("main", {"gamma": g, "alpha0": a0}, "similarity", s,
                               delta_h_pref=-0.3 - 0.001 * (s % 3)))
        for s in range(10):
            rs.append(_rec("driftform", {"alpha0": a0}, "random", s, delta_h_pref=-0.1))
            rs.append(_rec("driftform", {"alpha0": a0}, "similarity", s,
                           delta_h_pref=(-0.12 if a0 == 1.0 else -0.4) - 0.001 * (s % 3)))
    v = analyse_exp002(rs)
    assert v["primary"]["h1_supported"]
    d = {x["alpha0"]: x for x in v["drift_form"]}
    assert d[1.0]["dependent_on_drift_form"] and d[1.0]["abs_below_sesoi"]
    assert not d[0.1]["dependent_on_drift_form"]


def test_forest_svg_renders():
    svg = forest_svg([{"label": "a", "mean": -0.1, "lo": -0.2, "hi": 0.0}], "t", "x")
    assert svg.startswith("<svg") and "circle" in svg


@pytest.mark.parametrize("name", ("EXP-001", "EXP-002", "EXP-003", "EXP-004"))
def test_analysis_script_end_to_end_on_stub_results(tmp_path, name):
    """The frozen configs' expansion runs through the whole analysis with a stub simulator
    (no simulation of any confirmatory config; the stub values are arbitrary)."""
    import importlib.util
    import json

    from pulse.manifest import REPO_ROOT
    from pulse.runner import execute, expand, load_experiment

    exp = load_experiment(REPO_ROOT / "experiments" / f"{name}.json")
    exp = {**exp, "label": "exploratory", "output_dir": "results/exploratory/stub"}

    def stub(cfg, seed):
        rng = np.random.default_rng(seed + len(cfg.ranker) + int(1000 * cfg.alpha0))
        m = {"h_exp": float(rng.uniform(0.5, 0.9)), "gini_exposure": 0.5, "relevance": 0.5,
             "miscalibration_kl": 0.1, "user_control": 0.0, "like_rate": 0.5,
             "delta_h_pref": float(rng.uniform(-0.5, 0.0))}
        return {"metrics": m, "diagnostics": {}}

    raw = execute(exp, out_dir=tmp_path / "raw", simulate_fn=stub)
    spec = importlib.util.spec_from_file_location("ae", REPO_ROOT / "scripts" / "analyse_experiment.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main(name, raw, tmp_path / "dest") == 0
    v = json.loads((tmp_path / "dest" / "verdict.json").read_text())
    assert v["n_runs"] == len(expand(exp)) and v["n_failed"] == 0
    assert v["primary"]["n"] == 20
    assert (tmp_path / "dest" / "figures" / f"{name}-FIG-C01.svg").exists()
    prov = json.loads((tmp_path / "dest" / "run_manifest.json").read_text())
    assert len(prov["runs"]) == v["n_runs"] and len(prov["raw_sha256"]) == v["n_runs"] + 2
