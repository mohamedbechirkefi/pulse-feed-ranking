# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Unit, golden and property tests for configuration, metrics and statistics."""
import math

import numpy as np
import pytest

from pulse.config import ConfigError, SimConfig, from_dict
from pulse.metrics import entropy, gini, gini_reference, miscalibration_kl, normalised_entropy
from pulse.stats import betainc, holm, paired_summary, t_cdf, t_ppf


# ---- configuration -------------------------------------------------------
@pytest.mark.parametrize("kw", [
    {"ranker": "tiktok"}, {"n_users": 0}, {"n_users": 2.5}, {"n_users": True}, {"n_topics": 1},
    {"pool_size": 5, "slate_size": 10}, {"n_items": 10, "pool_size": 50}, {"window": 300},
    {"beta": 0.0}, {"beta": 1.5}, {"tau": 0.0}, {"eta": -0.1}, {"eta": 1.1}, {"gamma": 2.0},
    {"alpha0": 0.0}, {"preference_model": "other"}, {"drift_form": "x"}, {"pool_skew": "x"},
    {"ridge_lambda": 0.0}, {"lambda_mmr": 1.5}, {"calib_alpha": 0.0}, {"tau": float("nan")},
    {"item_noise": float("inf")},
])
def test_invalid_config_rejected(kw):
    with pytest.raises(ConfigError):
        SimConfig(**kw)


def test_unknown_key_rejected():
    with pytest.raises(ConfigError):
        from_dict({"n_user": 3})


def test_config_hash_stable_and_sensitive():
    a, b = SimConfig(), SimConfig()
    assert a.config_hash() == b.config_hash() and len(a.config_hash()) == 64
    assert a.config_hash() != a.with_overrides(eta=0.2).config_hash()


# ---- metrics: golden values ----------------------------------------------
def test_entropy_golden():
    assert entropy(np.array([0.5, 0.5])) == pytest.approx(math.log(2))
    assert entropy(np.array([1.0, 0.0, 0.0])) == 0.0  # 0 ln 0 = 0
    assert normalised_entropy(np.array([0.25] * 4)) == pytest.approx(1.0)
    # H([0.5, 0.25, 0.25]) = 1.5 ln 2 = 1.039721; / ln 3 = 0.946395
    assert entropy(np.array([0.5, 0.25, 0.25])) == pytest.approx(1.5 * math.log(2))
    assert normalised_entropy(np.array([0.5, 0.25, 0.25])) == pytest.approx(0.946395, abs=1e-6)
    # unnormalised weights are normalised first
    assert normalised_entropy(np.array([2.0, 2.0])) == pytest.approx(1.0)


def test_entropy_invalid():
    with pytest.raises(ValueError):
        entropy(np.array([-0.1, 1.1]))
    with pytest.raises(ValueError):
        entropy(np.array([0.0, 0.0]))
    with pytest.raises(ValueError):
        normalised_entropy(np.array([1.0]))


def test_gini_golden():
    assert gini(np.array([1, 1, 1, 1])) == 0.0
    assert gini(np.array([0, 0, 0, 1])) == pytest.approx(0.75)  # 6 / (2 * 4 * 1)
    assert gini(np.array([1, 2, 3])) == pytest.approx(8 / 36)


def test_gini_invalid():
    for bad in ([], [0, 0], [-1, 2]):
        with pytest.raises(ValueError):
            gini(np.array(bad))


def test_gini_differential_and_properties():
    rng = np.random.default_rng(1)
    for _ in range(200):
        c = rng.integers(0, 20, size=rng.integers(1, 40))
        if c.sum() == 0:
            continue
        g = gini(c)
        assert g == pytest.approx(gini_reference(c), abs=1e-12)
        assert 0.0 <= g <= 1.0 - 1.0 / c.size + 1e-12  # upper bound (N-1)/N
        assert gini(rng.permutation(c)) == pytest.approx(g)  # permutation invariance
        assert gini(3 * c) == pytest.approx(g)  # scale invariance


def test_normalised_entropy_bounds_property():
    rng = np.random.default_rng(2)
    p = rng.dirichlet(np.full(10, 0.3), size=500)
    h = normalised_entropy(p)
    assert np.all(h >= 0) and np.all(h <= 1 + 1e-12)


def test_miscalibration_golden_and_invalid():
    # p = [1, 0], q = [0, 1], alpha = 0.01: KL = ln(1 / 0.01) = ln 100
    assert miscalibration_kl(np.array([1.0, 0.0]), np.array([0.0, 1.0]), 0.01) == pytest.approx(math.log(100))
    p = np.array([0.2, 0.3, 0.5])
    assert miscalibration_kl(p, p, 0.01) == pytest.approx(0.0, abs=1e-15)
    with pytest.raises(ValueError):
        miscalibration_kl(p, p[:2], 0.01)
    with pytest.raises(ValueError):
        miscalibration_kl(p, p, 0.0)


def test_miscalibration_nonnegative_property():
    rng = np.random.default_rng(3)
    p = rng.dirichlet(np.ones(10), size=300)
    q = rng.dirichlet(np.ones(10), size=300)
    assert np.all(miscalibration_kl(p, q, 0.01) >= -1e-12)


# ---- statistics -----------------------------------------------------------
@pytest.mark.parametrize("df,expected", [(1, 12.706205), (2, 4.302653), (9, 2.262157), (19, 2.093024), (30, 2.042272)])
def test_t_ppf_against_tables(df, expected):
    assert t_ppf(0.975, df) == pytest.approx(expected, abs=1e-5)


def test_t_cdf_symmetry_and_betainc_edges():
    assert t_cdf(0.0, 5) == pytest.approx(0.5)
    assert t_cdf(1.3, 7) + t_cdf(-1.3, 7) == pytest.approx(1.0)
    assert betainc(2, 3, 0.0) == 0.0 and betainc(2, 3, 1.0) == 1.0
    assert betainc(1, 1, 0.3) == pytest.approx(0.3)  # uniform
    with pytest.raises(ValueError):
        t_ppf(1.0, 3)
    with pytest.raises(ValueError):
        t_cdf(1.0, 0)


def test_paired_summary_golden():
    # d = [1, 2, 3]: mean 2, sd 1, half-width t_{0.975,2} / sqrt(3) = 2.484138
    s = paired_summary([1.0, 2.0, 3.0], [0.0, 0.0, 0.0])
    assert s.n == 3 and s.mean_diff == pytest.approx(2.0) and s.sd_diff == pytest.approx(1.0)
    assert s.t_lo == pytest.approx(2 - 2.484138, abs=1e-5) and s.t_hi == pytest.approx(2 + 2.484138, abs=1e-5)
    assert s.d_z == pytest.approx(2.0)
    assert 1.0 <= s.boot_lo <= s.boot_hi <= 3.0


def test_paired_summary_is_paired_not_pooled():
    # Large between-seed variation cancels in the pairing.
    a = np.array([10.0, 20.0, 30.0, 40.0]) + 0.1
    b = np.array([10.0, 20.0, 30.0, 40.0])
    s = paired_summary(a, b)
    assert s.mean_diff == pytest.approx(0.1) and s.sd_diff == pytest.approx(0.0, abs=1e-12)


def test_paired_summary_invalid():
    with pytest.raises(ValueError):
        paired_summary([1.0, 2.0], [1.0])
    with pytest.raises(ValueError):
        paired_summary([1.0, float("nan")], [1.0, 2.0])
    with pytest.raises(ValueError):
        paired_summary([], [])
    one = paired_summary([1.0], [0.0])
    assert one.t_lo is None and one.mean_diff == 1.0


def test_holm_golden():
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([None, 0.5]) == [None, 0.5]
    assert holm([0.6, 0.6]) == [1.0, 1.0]
