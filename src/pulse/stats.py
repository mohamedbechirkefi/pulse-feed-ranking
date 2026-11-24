# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Paired-seed uncertainty (protocol section 7) with no dependency beyond numpy.

Student t quantiles use the regularised incomplete beta function (continued fraction,
Lentz's method) and bisection; tests check them against published table values.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np

BOOTSTRAP_SEED = 20261124
BOOTSTRAP_RESAMPLES = 10_000


def _betacf(a: float, b: float, x: float) -> float:
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta I_x(a, b)."""
    if not 0.0 <= x <= 1.0:
        raise ValueError("x must be in [0, 1]")
    if x in (0.0, 1.0):
        return x
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: int) -> float:
    if df < 1:
        raise ValueError("df must be >= 1")
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_ppf(p: float, df: int) -> float:
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


@dataclass(frozen=True)
class PairedSummary:
    n: int
    mean_diff: float
    sd_diff: float | None
    t_lo: float | None
    t_hi: float | None
    boot_lo: float | None
    boot_hi: float | None
    d_z: float | None
    p_two_sided: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def paired_summary(treat, control, level: float = 0.95, n_boot: int = BOOTSTRAP_RESAMPLES,
                   boot_seed: int = BOOTSTRAP_SEED) -> PairedSummary:
    """Mean paired difference treat - control over seeds, t-interval, percentile bootstrap, d_z."""
    a = np.asarray(treat, dtype=float)
    b = np.asarray(control, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("treat and control must be 1-D arrays of equal length (paired by seed)")
    if np.any(~np.isfinite(a)) or np.any(~np.isfinite(b)):
        raise ValueError("non-finite value in paired data")
    d = a - b
    n = d.size
    if n == 0:
        raise ValueError("no pairs")
    m = float(d.mean())
    if n < 2:
        return PairedSummary(n, m, None, None, None, None, None, None, None)
    sd = float(d.std(ddof=1))
    half = t_ppf(0.5 + level / 2, n - 1) * sd / math.sqrt(n)
    rng = np.random.default_rng(boot_seed)
    means = d[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    alpha = (1 - level) / 2
    blo, bhi = np.quantile(means, [alpha, 1 - alpha])
    if sd > 0:
        tstat = m / (sd / math.sqrt(n))
        p = 2 * (1 - t_cdf(abs(tstat), n - 1))
        dz = m / sd
    else:
        p, dz = None, None
    return PairedSummary(n, m, sd, m - half, m + half, float(blo), float(bhi), dz, p)


def holm(pvalues: list[float | None]) -> list[float | None]:
    """Holm step-down adjusted p-values; None entries are passed through and not counted."""
    idx = [i for i, p in enumerate(pvalues) if p is not None]
    m = len(idx)
    order = sorted(idx, key=lambda i: pvalues[i])
    adj: list[float | None] = list(pvalues)
    running = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvalues[i])
        running = max(running, val)
        adj[i] = running
    return adj
