# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""The interaction loop (protocol section 2). Deterministic given (config, master seed).

Per step t, for all users at once:
 1. draw the candidate pool (stream "pools"), and per (user, pool slot) tie keys ("tiebreak");
 2. the ranker returns a slate of k pool items;
 3. examination: position j (0-based) is examined if u < beta^j ("examination");
 4. true like if u < sigmoid((r_ui - c) / tau), c = like_midpoint, r_ui at the current p_u(t) ("choice");
 5. observed feedback = true like flipped with probability eta ("noise");
 6. the ranker updates on examined items' observed feedback;
 7. drifting model: p_u moves toward the topic of each truly liked examined item, in slate order.
All draws in 1, 3, 4 and 5 have fixed shapes, so arms with the same seed share them exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .config import SimConfig
from .metrics import gini, miscalibration_kl, normalised_entropy
from .model import (
    drift,
    initial_preferences,
    like_probability,
    make_catalog,
    sample_pools,
    spawn_streams,
    topic_distribution,
    utility,
)
from .rankers import make_ranker

SIMPLEX_TOL = 1e-9


class InvariantError(AssertionError):
    """A built-in invariant check failed; the run is excluded under protocol section 8."""


@dataclass
class Trace:
    """Optional per-step trace for tests and diagnostics (small configs only)."""

    slates: list[np.ndarray] = field(default_factory=list)
    examined: list[np.ndarray] = field(default_factory=list)
    observed: list[np.ndarray] = field(default_factory=list)
    prefs: list[np.ndarray] = field(default_factory=list)


def simulate(cfg: SimConfig, master_seed: int, trace: Trace | None = None) -> dict[str, Any]:
    """Run one simulation and return the run-level metrics and diagnostics (plain Python types)."""
    rng = spawn_streams(master_seed)
    cat = make_catalog(cfg, rng["catalog"])
    p0 = initial_preferences(cfg, rng["users"])
    pref = p0.copy()
    ranker = make_ranker(cfg)

    U, K, k, T, W = cfg.n_users, cfg.n_topics, cfg.slate_size, cfg.n_steps, cfg.window
    pos_w = cfg.beta ** np.arange(k)
    rows = np.arange(U)[:, None]

    topic_w = np.zeros((U, K))  # position-weighted topic exposure, final window
    exposure = np.zeros(cfg.n_items, dtype=np.int64)  # slate appearances, final window
    rel_sum = 0.0
    n_exam_w = 0
    n_like_w = 0
    ctrl_sum = 0.0
    ctrl_events = 0
    prev_share = None
    prev_dislike = None
    pool_topic_counts = np.zeros(K)

    for t in range(T):
        pool = sample_pools(cfg, rng["pools"])
        tie = rng["tiebreak"].random(pool.shape)
        u_exam = rng["examination"].random((U, k))
        u_like = rng["choice"].random((U, k))
        u_flip = rng["noise"].random((U, k))

        pool_emb = cat.emb[pool]
        order = ranker.rank(pool, pool_emb, tie)
        slate = pool[rows, order]
        srt = np.sort(slate, axis=1)
        if np.any(srt[:, 1:] == srt[:, :-1]):
            raise InvariantError(f"duplicate item in a slate at step {t}")

        z = cat.topics[slate]
        r = utility(pref, cat.pos_share[slate])
        examined = u_exam < pos_w[None, :]
        true_like = u_like < like_probability(r, cfg.tau, cfg.like_midpoint)
        observed = true_like ^ (u_flip < cfg.eta)

        ranker.update(slate, cat.emb[slate], examined, observed)

        share = np.zeros((U, K))
        np.add.at(share, (np.repeat(np.arange(U), k), z.ravel()), 1.0 / k)
        dislike = np.zeros((U, K))
        dmask = examined & ~observed
        np.add.at(dislike, (np.nonzero(dmask)[0], z[dmask]), 1.0)
        if prev_share is not None:
            ctrl_sum += float(np.sum(prev_dislike * (share - prev_share)))
            ctrl_events += int(prev_dislike.sum())
        prev_share, prev_dislike = share, dislike

        if t >= T - W:
            np.add.at(topic_w, (np.repeat(np.arange(U), k), z.ravel()), np.tile(pos_w, U))
            np.add.at(exposure, slate.ravel(), 1)
            rel_sum += float(r[examined].sum())
            n_exam_w += int(examined.sum())
            n_like_w += int((examined & observed).sum())
            np.add.at(pool_topic_counts, cat.topics[pool].ravel(), 1.0)

        if trace is not None:
            trace.slates.append(slate.copy())
            trace.examined.append(examined.copy())
            trace.observed.append(observed.copy())
            trace.prefs.append(pref.copy())

        if cfg.preference_model == "drifting" and cfg.gamma > 0:
            liked = examined & true_like
            for j in range(k):
                pref = drift(pref, z[:, j], liked[:, j], cfg.gamma, cfg.drift_form)
        s = pref.sum(axis=1)
        if np.any(pref < 0) or np.any(np.abs(s - 1.0) > SIMPLEX_TOL):
            raise InvariantError(f"preference left the simplex at step {t}")

    q = topic_w / topic_w.sum(axis=1, keepdims=True)
    h_exp_u = normalised_entropy(topic_w)
    h_exp = float(h_exp_u.mean())
    if not 0.0 - 1e-12 <= h_exp <= 1.0 + 1e-12:
        raise InvariantError("H_exp outside [0, 1]")
    out: dict[str, Any] = {
        "h_exp": h_exp,
        "gini_exposure": gini(exposure),
        "relevance": rel_sum / n_exam_w if n_exam_w else None,
        "miscalibration_kl": float(miscalibration_kl(pref, q, cfg.calib_alpha).mean()),
        "user_control": ctrl_sum / ctrl_events if ctrl_events else None,
        "like_rate": n_like_w / n_exam_w if n_exam_w else None,
        "delta_h_pref": (
            float((normalised_entropy(pref) - normalised_entropy(p0)).mean())
            if cfg.preference_model == "drifting"
            else None
        ),
    }
    diagnostics = {
        "h_exp_user_sd": float(h_exp_u.std()),
        "n_examined_window": n_exam_w,
        "n_likes_window": n_like_w,
        "n_dislike_events": ctrl_events,
        "catalog_topic_entropy": float(normalised_entropy(np.bincount(cat.topics, minlength=K).astype(float))),
        "pool_topic_entropy_window": float(normalised_entropy(pool_topic_counts)),
        "design_topic_entropy": float(normalised_entropy(topic_distribution(cfg))),
        "initial_pref_entropy": float(normalised_entropy(p0).mean()),
        "final_pref_entropy": float(normalised_entropy(pref).mean()),
        "distinct_items_exposed_window": int((exposure > 0).sum()),
    }
    for name, v in out.items():
        if v is not None and not np.isfinite(v):
            raise InvariantError(f"non-finite metric {name}")
    return {"metrics": out, "diagnostics": diagnostics}
