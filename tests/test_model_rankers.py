# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""World generation and rankers: golden examples, ties, feedback updates, zero feedback."""
import numpy as np
import pytest

from pulse.config import SimConfig
from pulse.model import (
    drift,
    initial_preferences,
    like_probability,
    make_catalog,
    sample_pools,
    spawn_streams,
    topic_distribution,
    utility,
)
from pulse.rankers import (
    LinUCBRanker,
    MMRRanker,
    PopularityRanker,
    RandomRanker,
    SimilarityRanker,
    cosine_to_items,
    make_ranker,
    order_by_score,
)


def tiny(**kw):
    base = dict(n_users=1, n_items=3, n_topics=2, pool_size=3, slate_size=3, n_steps=1, window=1)
    base.update(kw)
    return SimConfig(**base)


# ---- streams and generation ----------------------------------------------
def test_streams_deterministic_and_independent():
    a, b = spawn_streams(7), spawn_streams(7)
    for name in a:
        assert np.array_equal(a[name].random(4), b[name].random(4))
    c = spawn_streams(7)
    assert not np.array_equal(c["pools"].random(4), c["choice"].random(4))
    with pytest.raises(ValueError):
        spawn_streams(-1)


def test_topic_distribution_golden():
    assert np.allclose(topic_distribution(SimConfig()), 0.1)
    z = topic_distribution(SimConfig(pool_skew="zipf", zipf_s=1.0, n_topics=3))
    # weights 1, 1/2, 1/3 normalised by 11/6
    assert np.allclose(z, [6 / 11, 3 / 11, 2 / 11])


@pytest.mark.parametrize("skew", ["uniform", "zipf"])
def test_catalog_topic_frequencies_match_design(skew):
    cfg = SimConfig(n_items=20000, pool_skew=skew)
    cat = make_catalog(cfg, np.random.default_rng(0))
    freq = np.bincount(cat.topics, minlength=10) / cfg.n_items
    assert np.allclose(freq, topic_distribution(cfg), atol=0.01)
    assert np.allclose(np.linalg.norm(cat.emb, axis=1), 1.0)
    assert np.allclose(cat.pos_share.sum(axis=1), 1.0) and np.all(cat.pos_share >= 0)
    # the primary topic is the largest embedding component for nearly every item at sigma = 0.3
    assert np.mean(cat.emb.argmax(axis=1) == cat.topics) > 0.9


def test_initial_preferences_on_simplex_even_when_concentrated():
    for a0 in (1.0, 0.1, 1e-3):
        p = initial_preferences(SimConfig(alpha0=a0), np.random.default_rng(1))
        assert p.shape == (200, 10) and np.all(p >= 0) and np.allclose(p.sum(axis=1), 1.0)


def test_pools_unique_sorted_in_range():
    cfg = SimConfig(n_users=30, n_items=60, pool_size=50)
    pools = sample_pools(cfg, np.random.default_rng(2))
    assert pools.shape == (30, 50)
    assert np.all(np.diff(pools, axis=1) > 0)  # sorted and unique
    assert pools.min() >= 0 and pools.max() < 60


def test_utility_and_like_probability_golden():
    pref = np.array([[0.7, 0.3]])
    share = np.array([[1.0, 0.0], [0.5, 0.5]])
    assert np.allclose(utility(pref, share), [[0.7, 0.5]])
    assert like_probability(np.array(0.5), 0.1) == pytest.approx(0.5)
    assert like_probability(np.array(0.6), 0.1) == pytest.approx(0.7310586, abs=1e-7)


def test_drift_golden():
    p = np.array([[0.5, 0.5, 0.0], [0.2, 0.3, 0.5]])
    z = np.array([2, 0])
    m = np.array([True, False])
    out = drift(p, z, m, 0.1, "convex")
    assert np.allclose(out[0], [0.45, 0.45, 0.10]) and np.allclose(out[1], p[1])
    out2 = drift(p, z, m, 0.1, "additive_clip")
    assert np.allclose(out2[0], np.array([0.5, 0.5, 0.1]) / 1.1)
    assert np.array_equal(drift(p, z, np.array([False, False]), 0.1, "convex"), p)
    with pytest.raises(ValueError):
        drift(p, z, m, 0.1, "other")


def test_drift_stays_on_simplex_property():
    rng = np.random.default_rng(5)
    p = rng.dirichlet(np.ones(10), size=50)
    for _ in range(500):
        p = drift(p, rng.integers(10, size=50), rng.random(50) < 0.5, 0.2, "convex")
    assert np.all(p >= 0) and np.allclose(p.sum(axis=1), 1.0)


# ---- ties ------------------------------------------------------------------
def test_near_equal_scores_are_ties():
    # differ only by floating-point round-off: the tie key decides
    scores = np.array([[0.5 + 1e-16, 0.5, 0.5 - 1e-16]])
    keys = np.array([[0.9, 0.1, 0.5]])
    assert order_by_score(scores, keys, 3).tolist() == [[1, 2, 0]]


def test_ties_broken_by_tie_key():
    scores = np.array([[1.0, 2.0, 1.0, 2.0]])
    keys = np.array([[0.9, 0.7, 0.1, 0.8]])
    # 2.0 items: idx1 (key 0.7) before idx3 (0.8); 1.0 items: idx2 (0.1) before idx0 (0.9)
    assert order_by_score(scores, keys, 4).tolist() == [[1, 3, 2, 0]]
    assert order_by_score(scores, keys, 2).tolist() == [[1, 3]]


def test_order_by_score_invalid():
    with pytest.raises(ValueError):
        order_by_score(np.zeros((1, 3)), np.zeros((1, 4)), 2)
    with pytest.raises(FloatingPointError):
        order_by_score(np.array([[np.nan, 1.0]]), np.zeros((1, 2)), 1)


def test_random_ranker_is_tie_key_order():
    keys = np.array([[0.3, 0.1, 0.2]])
    assert RandomRanker(tiny(), 3).rank(None, None, keys).tolist() == [[1, 2, 0]]


# ---- zero feedback ----------------------------------------------------------
def zero_feedback_slates():
    cfg = SimConfig(n_users=4, n_items=40, pool_size=12, slate_size=5)
    cat = make_catalog(cfg, np.random.default_rng(0))
    pool = sample_pools(cfg, np.random.default_rng(1))
    keys = np.random.default_rng(2).random(pool.shape)
    out = {}
    for name in ("random", "popularity", "similarity", "linucb"):
        out[name] = make_ranker(cfg.with_overrides(ranker=name)).rank(pool, cat.emb[pool], keys)
    out["mmr"] = make_ranker(cfg.with_overrides(ranker="mmr")).rank(pool, cat.emb[pool], keys)
    return out, keys


def test_zero_feedback_rankers_fall_back_to_tie_order():
    out, keys = zero_feedback_slates()
    for name in ("popularity", "similarity", "linucb"):
        assert np.array_equal(out[name], out["random"]), name
    # MMR with zero relevance: first pick is the lowest tie key
    assert np.array_equal(out["mmr"][:, 0], keys.argmin(axis=1))


def test_cosine_zero_profile_is_zero():
    emb = np.ones((2, 3, 2)) / np.sqrt(2)
    s = cosine_to_items(np.array([[0.0, 0.0], [1.0, 0.0]]), emb)
    assert np.all(s[0] == 0.0) and np.allclose(s[1], 1 / np.sqrt(2))


# ---- feedback updates ---------------------------------------------------------
def test_popularity_update_counts_only_examined_observed_likes():
    r = PopularityRanker(tiny(n_users=2, n_items=5, pool_size=3), 5)
    slate = np.array([[0, 1, 2], [2, 3, 4]])
    examined = np.array([[True, True, False], [True, False, True]])
    liked = np.array([[True, False, True], [True, True, False]])
    r.update(slate, None, examined, liked)
    assert r.likes.tolist() == [1, 0, 1, 0, 0]


def test_similarity_update_golden():
    r = SimilarityRanker(tiny(), 3)
    emb = np.array([[[1.0, 0.0], [0.0, 1.0], [0.6, 0.8]]])
    r.update(None, emb, np.array([[True, True, False]]), np.array([[True, False, True]]))
    assert np.allclose(r.profile, [[1.0, -1.0]])  # like e0, dislike e1, e2 unexamined


def test_mmr_golden_hand_computed():
    # profile [1, 0.2]; rel = cos = [0.980581, 0.902134, 0.196116] for a=[1,0], b=[.8,.6], c=[0,1].
    # step 1: a. step 2: b -> 0.5*0.902134 - 0.5*0.8 = 0.051067; c -> 0.5*0.196116 - 0 = 0.098058: c.
    r = MMRRanker(tiny(ranker="mmr"), 3)
    r.profile[:] = [1.0, 0.2]
    emb = np.array([[[1.0, 0.0], [0.8, 0.6], [0.0, 1.0]]])
    keys = np.array([[0.5, 0.5, 0.5]])
    assert r.rank(None, emb, keys).tolist() == [[0, 2, 1]]
    s = SimilarityRanker(tiny(), 3)
    s.profile[:] = [1.0, 0.2]
    assert s.rank(None, emb, keys).tolist() == [[0, 1, 2]]


def test_mmr_lambda_one_equals_similarity_differential():
    cfg = SimConfig(n_users=20, n_items=100, pool_size=30, slate_size=10, lambda_mmr=1.0)
    rng = np.random.default_rng(9)
    cat = make_catalog(cfg, rng)
    pool = sample_pools(cfg, rng)
    keys = rng.random(pool.shape)
    prof = rng.normal(size=(20, 10))
    m, s = MMRRanker(cfg, 100), SimilarityRanker(cfg, 100)
    m.profile[:] = prof
    s.profile[:] = prof
    assert np.array_equal(m.rank(pool, cat.emb[pool], keys), s.rank(pool, cat.emb[pool], keys))


def test_mmr_slate_has_no_duplicates():
    cfg = SimConfig(n_users=10, n_items=100, pool_size=30, slate_size=10, lambda_mmr=0.0)
    rng = np.random.default_rng(4)
    cat = make_catalog(cfg, rng)
    pool = sample_pools(cfg, rng)
    out = MMRRanker(cfg, 100).rank(pool, cat.emb[pool], rng.random(pool.shape))
    assert all(len(set(row)) == 10 for row in out.tolist())


def test_linucb_sherman_morrison_matches_direct_inverse():
    cfg = SimConfig(n_users=3, n_items=50, pool_size=10, slate_size=4, ridge_lambda=1.0, alpha_ucb=0.7)
    rng = np.random.default_rng(11)
    r = LinUCBRanker(cfg, 50)
    A = np.repeat(np.eye(10)[None], 3, axis=0)
    b = np.zeros((3, 10))
    for _ in range(20):
        x = rng.normal(size=(3, 4, 10))
        x /= np.linalg.norm(x, axis=2, keepdims=True)
        ex = rng.random((3, 4)) < 0.7
        lk = rng.random((3, 4)) < 0.4
        r.update(None, x, ex, lk)
        for u in range(3):
            for j in range(4):
                if ex[u, j]:
                    A[u] += np.outer(x[u, j], x[u, j])
                    b[u] += lk[u, j] * x[u, j]
    assert np.allclose(r.A_inv, np.linalg.inv(A), atol=1e-10)
    assert np.allclose(r.b, b)
    # differential score check against a direct formula
    pe = rng.normal(size=(3, 10, 10))
    theta = np.linalg.solve(A, b[..., None])[..., 0]
    direct = np.einsum("ucd,ud->uc", pe, theta) + 0.7 * np.sqrt(np.einsum("ucd,ude,uce->uc", pe, np.linalg.inv(A), pe))
    assert np.allclose(r.scores(pe), direct)


def test_linucb_zero_feedback_scores_equal_for_unit_items():
    cfg = SimConfig(n_users=2, n_items=50, pool_size=5, slate_size=3, alpha_ucb=1.0, ridge_lambda=4.0)
    rng = np.random.default_rng(3)
    x = rng.normal(size=(2, 5, 10))
    x /= np.linalg.norm(x, axis=2, keepdims=True)
    assert np.allclose(LinUCBRanker(cfg, 50).scores(x), 0.5)  # alpha / sqrt(lambda)


def test_unknown_ranker():
    cfg = SimConfig()
    object.__setattr__(cfg, "ranker", "nope")
    with pytest.raises(ValueError):
        make_ranker(cfg)
