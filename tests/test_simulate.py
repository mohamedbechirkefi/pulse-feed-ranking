# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Simulation loop: seed determinism, common random numbers, preference models, reference recomputation."""
import numpy as np
import pytest

from pulse.config import SimConfig
from pulse.metrics import normalised_entropy
from pulse.model import make_catalog, spawn_streams
from pulse.simulate import Trace, simulate

SMALL = dict(n_users=20, n_items=200, pool_size=30, slate_size=5, n_steps=30, window=10)
RANKERS = ("random", "popularity", "similarity", "linucb", "mmr")


@pytest.mark.parametrize("ranker", RANKERS)
def test_seed_determinism(ranker):
    cfg = SimConfig(ranker=ranker, **SMALL)
    assert simulate(cfg, 123) == simulate(cfg, 123)
    assert simulate(cfg, 123)["metrics"] != simulate(cfg, 124)["metrics"]


@pytest.mark.parametrize("ranker", RANKERS)
def test_metric_bounds(ranker):
    for pm, g in (("static", 0.0), ("drifting", 0.1)):
        m = simulate(SimConfig(ranker=ranker, preference_model=pm, gamma=g, eta=0.1, **SMALL), 5)["metrics"]
        assert 0 <= m["h_exp"] <= 1 and 0 <= m["gini_exposure"] <= 1 and 0 <= m["relevance"] <= 1
        assert 0 <= m["like_rate"] <= 1 and m["miscalibration_kl"] >= 0
        assert (m["delta_h_pref"] is None) == (pm == "static")


def test_common_random_numbers_across_arms():
    """Same seed: identical candidate pools and examination draws in every arm."""
    traces = {}
    for r in ("random", "similarity"):
        tr = Trace()
        simulate(SimConfig(ranker=r, **SMALL), 9, trace=tr)
        traces[r] = tr
    for a, b in zip(traces["random"].examined, traces["similarity"].examined):
        assert np.array_equal(a, b)
    # slates come from the same pools: the first step (zero feedback) is identical
    assert np.array_equal(traces["random"].slates[0], traces["similarity"].slates[0])


def test_static_preferences_never_change():
    tr = Trace()
    simulate(SimConfig(ranker="similarity", **SMALL), 1, trace=tr)
    assert all(np.array_equal(tr.prefs[0], p) for p in tr.prefs)


def test_drifting_preferences_concentrate_and_stay_on_simplex():
    tr = Trace()
    cfg = SimConfig(ranker="similarity", preference_model="drifting", gamma=0.2, tau=0.3, **SMALL)
    out = simulate(cfg, 1, trace=tr)
    for p in tr.prefs:
        assert np.all(p >= 0) and np.allclose(p.sum(axis=1), 1.0)
    assert out["metrics"]["delta_h_pref"] < 0


def test_zero_gamma_drift_is_static():
    a = simulate(SimConfig(ranker="mmr", preference_model="drifting", gamma=0.0, **SMALL), 3)
    assert a["metrics"]["delta_h_pref"] == 0.0


def test_h_exp_matches_naive_reference():
    """Differential: recompute final-window H_exp with plain Python loops from the trace."""
    cfg = SimConfig(ranker="popularity", eta=0.1, **SMALL)
    tr = Trace()
    out = simulate(cfg, 77, trace=tr)
    cat = make_catalog(cfg, spawn_streams(77)["catalog"])
    vals = []
    for u in range(cfg.n_users):
        w = [0.0] * cfg.n_topics
        for t in range(cfg.n_steps - cfg.window, cfg.n_steps):
            for j, item in enumerate(tr.slates[t][u]):
                w[cat.topics[item]] += cfg.beta ** j
        vals.append(float(normalised_entropy(np.array(w))))
    assert out["metrics"]["h_exp"] == pytest.approx(np.mean(vals), abs=1e-12)


def test_like_rate_matches_trace():
    cfg = SimConfig(ranker="similarity", eta=0.2, **SMALL)
    tr = Trace()
    out = simulate(cfg, 8, trace=tr)
    ex = np.array(tr.examined[-cfg.window:])
    ob = np.array(tr.observed[-cfg.window:])
    assert out["metrics"]["like_rate"] == pytest.approx((ex & ob).sum() / ex.sum())


def test_random_arm_exposure_tracks_catalog_topic_distribution():
    """Topic distributions: under random ranking exposure entropy is close to the pool entropy."""
    for skew in ("uniform", "zipf"):
        d = simulate(SimConfig(ranker="random", pool_skew=skew, n_users=50, n_items=1000, n_steps=60, window=40), 4)
        diag = d["diagnostics"]
        assert abs(diag["pool_topic_entropy_window"] - diag["design_topic_entropy"]) < 0.02
        # per-user windows are finite samples, so per-user entropy sits a little below the pool entropy
        assert 0 < diag["pool_topic_entropy_window"] - d["metrics"]["h_exp"] < 0.05


def test_full_noise_eta_one_inverts_feedback():
    """eta = 1 flips every observation: observed likes are exactly the true dislikes."""
    cfg = SimConfig(ranker="random", eta=1.0, **SMALL)
    a = simulate(cfg, 2)["metrics"]["like_rate"]
    b = simulate(cfg.with_overrides(eta=0.0), 2)["metrics"]["like_rate"]
    assert a == pytest.approx(1.0 - b)
