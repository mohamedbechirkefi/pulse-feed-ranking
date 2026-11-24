# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Ingestion (protocol 15.2 to 15.6) on a committed synthetic fixture, calibration (15.5), config
extensions and the user-control family rule (15.7). No test reads real MovieLens data."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from pulse.calibrate import file_users, fit_midpoint, mean_like, utilities
from pulse.config import ConfigError, SimConfig
from pulse.model import (
    PreferenceFileError,
    initial_preferences,
    like_probability,
    load_preference_file,
    topic_distribution,
)
from pulse.movielens import (
    IngestError,
    choose_topics,
    ingest,
    parse_movies,
    parse_ratings,
    preference_vectors,
    primary_topic,
)
from pulse.report import contrasts

FIX = Path(__file__).parent / "fixtures" / "movielens"
MOVIES = (FIX / "movies.dat").read_text()
RATINGS = (FIX / "ratings.dat").read_text()


def test_fixture_ingests_with_counts_and_schema():
    res = ingest(MOVIES, RATINGS)
    c = res.counts
    assert len(res.topics) == 10 and len(set(res.topics)) == 10
    assert c["movies_bad_rows"] == 0 and c["ratings_bad_rows"] == 0
    assert c["movies_included"] + c["movies_excluded_no_topic"] == c["movies_valid"]
    assert c["ratings_excluded_unknown_movie"] == 1
    assert (c["ratings_included"] + c["ratings_excluded_unknown_movie"] + c["ratings_excluded_no_topic"]
            == c["ratings_valid"])
    assert c["ratings_included_calibration"] + c["ratings_included_heldout"] == c["ratings_included"]
    assert c["users_calibration"] == res.prefs_calibration.shape[0] == 10
    assert c["users_heldout"] == res.prefs_heldout.shape[0] == 10
    assert np.isclose(res.pi.sum(), 1.0) and np.all(res.pi >= 0)
    for P in (res.prefs_calibration, res.prefs_heldout):
        assert P.shape[1] == 10 and np.allclose(P.sum(axis=1), 1.0) and np.all(P > 0)


def test_like_rate_uses_calibration_half_only():
    res = ingest(MOVIES, RATINGS)
    r, _, _ = parse_ratings(RATINGS)
    incl = np.array([m in res.movie_topic for m in r[:, 1]])
    odd = r[:, 0] % 2 == 1
    assert res.like_rate_calibration == pytest.approx(float((r[incl & odd, 2] >= 4).mean()))
    # changing only held-out (even) ratings leaves L* unchanged
    lines = [ln if int(ln.split("::")[0]) % 2 else "::".join(ln.split("::")[:2] + ["1"] + ln.split("::")[3:])
             for ln in RATINGS.splitlines()]
    assert ingest(MOVIES, "\n".join(lines)).like_rate_calibration == res.like_rate_calibration


def test_ingestion_is_deterministic():
    a, b = ingest(MOVIES, RATINGS), ingest(MOVIES, RATINGS)
    assert np.array_equal(a.prefs_heldout, b.prefs_heldout) and a.topics == b.topics


def test_topic_rules_golden():
    movies = {1: ("Drama",), 2: ("Drama", "Comedy"), 3: ("Comedy", "War"), 4: ("Western",)}
    topics, cnt = choose_topics(movies, k=3)
    assert topics == ["Comedy", "Drama", "War"]  # 2, 2 (alphabetical tie), 1; Western ties War, loses alphabetically
    assert primary_topic(("Drama", "Comedy"), topics, cnt) == topics.index("Comedy")  # tie on count -> alphabetical
    assert primary_topic(("Comedy", "War"), topics, cnt) == topics.index("War")  # fewer movies wins
    assert primary_topic(("Western",), topics, cnt) is None


def test_preference_vectors_golden():
    p = preference_vectors(np.array([[1.0, 0.0]]), np.array([0.5, 0.5]))
    assert np.allclose(p, [[2 / 3, 1 / 3]])
    p = preference_vectors(np.array([[0.0, 0.0]]), np.array([0.8, 0.2]))
    assert np.allclose(p, [[0.2, 0.8]])  # availability removed: the rare topic gets the larger weight
    with pytest.raises(IngestError):
        preference_vectors(np.zeros((1, 2)), np.array([1.0, 0.0]))


def test_schema_failures_counted_and_limit_enforced():
    _, rows, bad = parse_movies(MOVIES + "x::y\n1::dup::Drama\n9999::Bad genre::Cartoons\n")
    assert bad == 3 and rows == 64
    _, rows, bad = parse_ratings("1::2::6::3\n1::2::x::3\n1::2::3\n1::2::4::5\n")
    assert (rows, bad) == (4, 3)
    with pytest.raises(IngestError):
        ingest(MOVIES + "garbage\n" * 5, RATINGS)
    with pytest.raises(IngestError):
        ingest(MOVIES, "")


def test_no_user_ids_in_outputs():
    res = ingest(MOVIES, RATINGS)
    assert not hasattr(res, "user_ids")
    assert set(vars(res)) == {"topics", "genre_movie_counts", "movie_topic", "pi", "counts",
                              "like_rate_calibration", "prefs_calibration", "prefs_heldout"}


# --- calibration (15.5) ---

def test_like_probability_midpoint():
    assert like_probability(np.array(0.2), 0.1, 0.2) == pytest.approx(0.5)
    assert like_probability(np.array(0.5), 0.1) == pytest.approx(0.5)


def test_fit_midpoint_recovers_target_and_is_monotone():
    cfg = SimConfig(n_users=30, n_items=80)
    rs = utilities(cfg, seeds=(1, 2))
    for tau, target in ((0.1, 0.55), (0.3, 0.2)):
        c = fit_midpoint(rs, tau, target)
        assert mean_like(rs, tau, c) == pytest.approx(target, abs=1e-6)
    assert mean_like(rs, 0.1, 0.0) > mean_like(rs, 0.1, 0.1) > mean_like(rs, 0.1, 0.2)
    with pytest.raises(ValueError):
        fit_midpoint(rs, 0.1, 1.0)


def test_calibration_uses_no_ranker(monkeypatch):
    import pulse.rankers as rk
    import pulse.simulate as sim

    def boom(*a, **k):
        raise AssertionError("calibration must not rank or simulate")
    monkeypatch.setattr(rk, "make_ranker", boom)
    monkeypatch.setattr(sim, "simulate", boom)
    rs = utilities(SimConfig(n_users=10, n_items=60), seeds=(3,))
    fit_midpoint(rs, 0.1, 0.5)


# --- config and file-sourced users (15.6) ---

def _pref_file(tmp_path, vectors):
    blob = (json.dumps({"vectors": vectors}) + "\n").encode()
    (tmp_path / "p.json").write_bytes(blob)
    return "p.json", hashlib.sha256(blob).hexdigest()


def test_custom_topic_weights_and_validation():
    w = [0.5, 0.3, 0.2]
    cfg = SimConfig(n_topics=3, pool_skew="custom", topic_weights=w)
    assert isinstance(cfg.topic_weights, tuple) and np.allclose(topic_distribution(cfg), w)
    cfg.config_hash()
    for bad in ({"pool_skew": "custom"}, {"pool_skew": "custom", "topic_weights": [0.5, 0.6, -0.1]},
                {"topic_weights": [0.5, 0.3, 0.2]}, {"user_source": "file"},
                {"user_pref_path": "x.json"}, {"user_source": "file", "user_pref_path": "x", "user_pref_sha256": "zz"}):
        with pytest.raises(ConfigError):
            SimConfig(n_topics=3, **bad)


def test_file_users_sampled_without_replacement_and_verified(tmp_path):
    vec = np.random.default_rng(0).dirichlet(np.ones(3), size=12)
    vec = (vec / vec.sum(axis=1, keepdims=True)).tolist()
    path, h = _pref_file(tmp_path, vec)
    V = load_preference_file(path, h, str(tmp_path))
    users = file_users(V)
    p = users(SimConfig(n_users=12, n_topics=3), np.random.default_rng(1))
    assert sorted(map(tuple, p.round(12))) == sorted(map(tuple, np.array(vec).round(12)))
    with pytest.raises(PreferenceFileError):
        load_preference_file(path, "0" * 64, str(tmp_path))
    with pytest.raises(ValueError):
        users(SimConfig(n_users=13, n_topics=3), np.random.default_rng(1))


def test_missing_preference_file_fails_clearly():
    cfg = SimConfig(user_source="file", user_pref_path="data/processed/nope.json", user_pref_sha256="a" * 64)
    with pytest.raises(PreferenceFileError):
        initial_preferences(cfg, np.random.default_rng(0))


# --- user control family (15.7) ---

def _res(arm, seed, uc, h):
    return {"status": "ok", "block": "main", "cell": {}, "arm": arm, "seed": seed,
            "metrics": {"h_exp": h, "gini_exposure": 0.1, "relevance": 0.1, "miscalibration_kl": 0.1,
                        "user_control": uc, "like_rate": 0.5, "delta_h_pref": None}}


def test_user_control_only_against_random():
    rs = []
    for s in range(4):
        rs += [_res("random", s, -0.09 + s * 1e-3, 0.9), _res("similarity", s, -0.2 + s * 2e-3, 0.8 + s * 1e-3),
               _res("mmr", s, -0.15 - s * 1e-3, 0.85 + s * 2e-3)]
    out = contrasts(rs)
    uc = {(r["treatment"], r["control"]) for r in out if r["metric"] == "user_control"}
    assert uc == {("similarity", "random"), ("mmr", "random")}
    hx = {(r["treatment"], r["control"]) for r in out if r["metric"] == "h_exp"}
    assert ("mmr", "similarity") in hx


def test_exp004_config_builds_a_world_when_data_present():
    """Uses the git-ignored processed file if present; checks only the world, never runs a ranker."""
    from pulse.config import from_dict
    from pulse.runner import load_experiment
    from pulse.manifest import REPO_ROOT
    from pulse.model import make_catalog, spawn_streams

    exp = load_experiment(REPO_ROOT / "experiments" / "EXP-004.json")
    if not (REPO_ROOT / exp["base"]["user_pref_path"]).exists():
        pytest.skip("MovieLens not prepared (scripts/download_movielens.py, scripts/prepare_movielens.py)")
    cfg = from_dict(exp["base"])
    rng = spawn_streams(1)  # not an EXP-004 seed
    p = initial_preferences(cfg, rng["users"])
    assert p.shape == (200, 10) and np.allclose(p.sum(axis=1), 1.0)
    assert make_catalog(cfg, rng["catalog"]).topics.shape == (1000,)
