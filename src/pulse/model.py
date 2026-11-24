# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Synthetic world generation (the ingestion layer of PULSE: all data are synthetic).

Pure functions of a config and explicit numpy Generators. No hidden global state.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import SimConfig

# Fixed order of spawned streams per master seed. Changing it changes every result.
STREAMS = ("catalog", "users", "pools", "examination", "choice", "noise", "tiebreak")


def spawn_streams(master_seed: int) -> dict[str, np.random.Generator]:
    """Independent streams per component, derived with SeedSequence.spawn (protocol section 6).

    Every arm with the same master seed receives identical streams, so catalog, users,
    candidate pools, examination, choice and noise draws are common random numbers.
    """
    if not isinstance(master_seed, (int, np.integer)) or isinstance(master_seed, bool) or master_seed < 0:
        raise ValueError(f"master_seed must be a non-negative int, got {master_seed!r}")
    children = np.random.SeedSequence(int(master_seed)).spawn(len(STREAMS))
    return {name: np.random.default_rng(ss) for name, ss in zip(STREAMS, children)}


def topic_distribution(cfg: SimConfig) -> np.ndarray:
    """Catalog topic distribution pi: uniform, or Zipf with pi_z proportional to 1 / z^s, z = 1..K."""
    K = cfg.n_topics
    if cfg.pool_skew == "uniform":
        return np.full(K, 1.0 / K)
    w = 1.0 / np.arange(1, K + 1, dtype=float) ** cfg.zipf_s
    return w / w.sum()


@dataclass(frozen=True)
class Catalog:
    topics: np.ndarray  # (N,) int primary topic z_i
    emb: np.ndarray  # (N, K) unit-norm embeddings e_i
    pos_share: np.ndarray  # (N, K) max(e_iz, 0) / sum_z max(e_iz, 0); rows sum to 1


def make_catalog(cfg: SimConfig, rng: np.random.Generator) -> Catalog:
    N, K = cfg.n_items, cfg.n_topics
    topics = rng.choice(K, size=N, p=topic_distribution(cfg))
    raw = cfg.item_signal * np.eye(K)[topics] + rng.normal(0.0, cfg.item_noise, size=(N, K))
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise FloatingPointError("zero-norm item embedding")
    emb = raw / norms
    pos = np.maximum(emb, 0.0)
    mass = pos.sum(axis=1, keepdims=True)
    # An item whose embedding has no positive component would have undefined utility.
    # With a = 1 and sigma = 0.3 this is practically impossible; fall back to its primary topic.
    bad = mass[:, 0] <= 0
    if np.any(bad):
        pos[bad] = np.eye(K)[topics[bad]]
        mass = pos.sum(axis=1, keepdims=True)
    return Catalog(topics=topics, emb=emb, pos_share=pos / mass)


def initial_preferences(cfg: SimConfig, rng: np.random.Generator) -> np.ndarray:
    """p_u(0) ~ Dirichlet(alpha0 * 1_K), shape (U, K). Rows renormalised against round-off."""
    p = rng.dirichlet(np.full(cfg.n_topics, cfg.alpha0), size=cfg.n_users)
    # Very small alpha0 can underflow every component of a row to zero.
    zero = p.sum(axis=1) <= 0
    if np.any(zero):
        p[zero] = np.eye(cfg.n_topics)[rng.integers(cfg.n_topics, size=int(zero.sum()))]
    return p / p.sum(axis=1, keepdims=True)


def utility(pref: np.ndarray, pos_share: np.ndarray) -> np.ndarray:
    """True utility r_ui = sum_z p_uz * pos_share_iz, in [0, 1].

    pref: (U, K); pos_share: (U, C, K) or (C, K). Returns (U, C).
    """
    if pos_share.ndim == 2:
        return pref @ pos_share.T
    return np.einsum("uk,uck->uc", pref, pos_share)


def sample_pools(cfg: SimConfig, rng: np.random.Generator) -> np.ndarray:
    """Candidate pools: C items per user uniformly without replacement, sorted ascending. (U, C)."""
    keys = rng.random((cfg.n_users, cfg.n_items))
    idx = np.argpartition(keys, cfg.pool_size - 1, axis=1)[:, : cfg.pool_size]
    return np.sort(idx, axis=1)


def like_probability(r: np.ndarray, tau: float) -> np.ndarray:
    """sigmoid((r - 0.5) / tau)."""
    return 1.0 / (1.0 + np.exp(-(r - 0.5) / tau))


def drift(pref: np.ndarray, topic: np.ndarray, mask: np.ndarray, gamma: float, form: str) -> np.ndarray:
    """Apply one like-driven drift update to the rows selected by mask. Returns a new array.

    convex:        p <- normalise((1 - gamma) p + gamma onehot(z))
    additive_clip: p <- normalise(clip(p + gamma onehot(z), 0, 1))
    """
    out = pref.copy()
    if not np.any(mask):
        return out
    K = pref.shape[1]
    oh = np.eye(K)[topic[mask]]
    if form == "convex":
        new = (1.0 - gamma) * pref[mask] + gamma * oh
    elif form == "additive_clip":
        new = np.clip(pref[mask] + gamma * oh, 0.0, 1.0)
    else:
        raise ValueError(f"unknown drift form {form!r}")
    out[mask] = new / new.sum(axis=1, keepdims=True)
    return out
