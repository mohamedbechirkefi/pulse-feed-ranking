# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Pure metric functions (protocol section 5, EXP-001 section 10). Convention: 0 ln 0 = 0."""
from __future__ import annotations

import numpy as np


def entropy(p: np.ndarray, axis: int = -1) -> np.ndarray:
    """Shannon entropy in nats of distributions along axis. Inputs must be nonnegative."""
    p = np.asarray(p, dtype=float)
    if np.any(p < 0):
        raise ValueError("entropy of a negative weight")
    s = p.sum(axis=axis, keepdims=True)
    if np.any(s <= 0):
        raise ValueError("entropy of an empty distribution")
    q = p / s
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(q > 0, q * np.log(q), 0.0)
    return -terms.sum(axis=axis)


def normalised_entropy(p: np.ndarray, axis: int = -1) -> np.ndarray:
    """Entropy divided by ln K, in [0, 1]."""
    K = np.asarray(p).shape[axis]
    if K < 2:
        raise ValueError("normalised entropy needs K >= 2")
    return entropy(p, axis=axis) / np.log(K)


def gini(counts: np.ndarray) -> float:
    """G = sum_i sum_j |c_i - c_j| / (2 N sum_i c_i), via the sorted-cumulative identity."""
    c = np.asarray(counts, dtype=float).ravel()
    if c.size == 0:
        raise ValueError("gini of an empty array")
    if np.any(c < 0):
        raise ValueError("gini of negative counts")
    total = c.sum()
    if total == 0:
        raise ValueError("gini of all-zero counts")
    n = c.size
    s = np.sort(c)
    i = np.arange(1, n + 1)
    return float(np.sum((2 * i - n - 1) * s) / (n * total))


def gini_reference(counts) -> float:
    """O(N^2) definition, used only by differential tests."""
    c = np.asarray(counts, dtype=float).ravel()
    return float(np.abs(c[:, None] - c[None, :]).sum() / (2 * c.size * c.sum()))


def miscalibration_kl(p: np.ndarray, q: np.ndarray, alpha: float) -> np.ndarray:
    """KL(p || (1 - alpha) q + alpha p) in nats, per row (Steck 2018 smoothing). Finite for alpha > 0."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if p.shape != q.shape:
        raise ValueError("p and q must have the same shape")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    qt = (1 - alpha) * q + alpha * p
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(p > 0, p * np.log(p / qt), 0.0)
    return terms.sum(axis=-1)
