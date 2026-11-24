# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Choice-curve calibration (research/protocol.md section 15.5).

c(tau) solves M(c) = L*, with M(c) the mean of sigmoid((r_ui - c) / tau) over all users and all
items of the synthetic worlds of the calibration seeds. Only the catalog and user generators are
used: no ranker, no interaction loop and no metric, so the fit cannot touch the primary contrast.
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from .config import SimConfig
from .model import like_probability, make_catalog, sample_file_preferences, spawn_streams, utility

CALIBRATION_SEEDS = tuple(range(700001, 700021))  # 20 seeds, disjoint from all run seeds
BRACKET = (-1.0, 2.0)
TOL = 1e-9


def utilities(cfg: SimConfig, seeds=CALIBRATION_SEEDS,
              users: Callable[[SimConfig, np.random.Generator], np.ndarray] | None = None) -> list[np.ndarray]:
    """r_ui for all users x all items of each calibration seed's world (catalog and users streams)."""
    from .model import initial_preferences

    out = []
    for s in seeds:
        rng = spawn_streams(s)
        cat = make_catalog(cfg, rng["catalog"])
        p = (users or initial_preferences)(cfg, rng["users"])
        out.append(utility(p, cat.pos_share))
    return out


def mean_like(rs: list[np.ndarray], tau: float, c: float) -> float:
    return float(np.mean([like_probability(r, tau, c).mean() for r in rs]))


def fit_midpoint(rs: list[np.ndarray], tau: float, target: float,
                 bracket: tuple[float, float] = BRACKET, tol: float = TOL) -> float:
    """Bisection for c with mean_like(c) = target; mean_like is strictly decreasing in c."""
    if not 0.0 < target < 1.0:
        raise ValueError("target like rate must be in (0, 1)")
    lo, hi = bracket
    if not mean_like(rs, tau, lo) >= target >= mean_like(rs, tau, hi):
        raise ValueError("target not bracketed")
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if mean_like(rs, tau, mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def file_users(vectors: np.ndarray) -> Callable[[SimConfig, np.random.Generator], np.ndarray]:
    """User generator sampling U vectors without replacement (EXP-004 calibration, section 15.6)."""
    return lambda cfg, rng: sample_file_preferences(vectors, cfg.n_users, rng)
