# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Ranking arms. Each ranker sees only the candidate pool, item embeddings and observed feedback.

Tie-breaking rule (one rule for every ranker, protocol section 2): scores are rounded to
SCORE_DECIMALS decimal places, then sorted descending; items with equal rounded scores are
ordered by ascending tie key, a uniform draw from the
shared "tiebreak" stream, one key per (user, pool position, step). The random ranker gives
every item the same score, so its slate is the tie-key order: a uniform random permutation.

Rounding (decision D-006): without it, LinUCB's cold-start scores alpha / sqrt(lambda), equal in
exact arithmetic, differ by about 1e-16 and the slate order was set by round-off instead of the
tie rule (found by test_zero_feedback_rankers_fall_back_to_tie_order during M2).
"""
from __future__ import annotations

from typing import Protocol

import numpy as np

from .config import SimConfig

SCORE_DECIMALS = 12


def quantise(scores: np.ndarray) -> np.ndarray:
    """Round scores so that values equal in exact arithmetic compare equal (tie rule)."""
    return np.round(scores, SCORE_DECIMALS)


def order_by_score(scores: np.ndarray, tie_keys: np.ndarray, k: int) -> np.ndarray:
    """Indices (U, k) into the pool: score descending, then tie key ascending."""
    if scores.shape != tie_keys.shape:
        raise ValueError("scores and tie_keys must have the same shape")
    if np.any(~np.isfinite(scores)):
        raise FloatingPointError("non-finite ranking score")
    return np.lexsort((tie_keys, -quantise(scores)), axis=-1)[:, :k]


def cosine_to_items(profile: np.ndarray, item_emb: np.ndarray) -> np.ndarray:
    """cos(v_u, e_i) for pool items. profile (U, K); item_emb (U, C, K) unit norm.

    A zero profile gives score 0 for every item (cold start), which leaves the order to the tie keys.
    """
    norm = np.linalg.norm(profile, axis=1)
    safe = np.where(norm > 0, norm, 1.0)
    dots = np.einsum("uk,uck->uc", profile, item_emb)
    out = dots / safe[:, None]
    out[norm == 0] = 0.0
    return out


class Ranker(Protocol):
    name: str

    def rank(self, pool: np.ndarray, pool_emb: np.ndarray, tie_keys: np.ndarray) -> np.ndarray: ...

    def update(self, slate: np.ndarray, slate_emb: np.ndarray, examined: np.ndarray, observed_like: np.ndarray) -> None: ...


class RandomRanker:
    name = "random"

    def __init__(self, cfg: SimConfig, n_items: int) -> None:
        self.k = cfg.slate_size

    def rank(self, pool, pool_emb, tie_keys):
        return order_by_score(np.zeros(tie_keys.shape), tie_keys, self.k)

    def update(self, slate, slate_emb, examined, observed_like):
        return None


class PopularityRanker:
    """Global observed like count per item to date, updated after each step for all users."""

    name = "popularity"

    def __init__(self, cfg: SimConfig, n_items: int) -> None:
        self.k = cfg.slate_size
        self.likes = np.zeros(n_items, dtype=np.int64)

    def rank(self, pool, pool_emb, tie_keys):
        return order_by_score(self.likes[pool].astype(float), tie_keys, self.k)

    def update(self, slate, slate_emb, examined, observed_like):
        liked = slate[examined & observed_like]
        np.add.at(self.likes, liked, 1)


class SimilarityRanker:
    """Profile v_u = sum of embeddings of observed likes minus observed dislikes; score = cosine."""

    name = "similarity"

    def __init__(self, cfg: SimConfig, n_items: int) -> None:
        self.k = cfg.slate_size
        self.profile = np.zeros((cfg.n_users, cfg.n_topics))

    def scores(self, pool_emb):
        return cosine_to_items(self.profile, pool_emb)

    def rank(self, pool, pool_emb, tie_keys):
        return order_by_score(self.scores(pool_emb), tie_keys, self.k)

    def update(self, slate, slate_emb, examined, observed_like):
        sign = np.where(observed_like, 1.0, -1.0) * examined
        self.profile += np.einsum("uj,ujk->uk", sign, slate_emb)


class MMRRanker(SimilarityRanker):
    """Maximal marginal relevance re-ranking of the similarity score (Carbonell and Goldstein 1998).

    Greedy: next = argmax_i lambda * rel_i - (1 - lambda) * max_{j selected} cos(e_i, e_j).
    Exact ties at each greedy step are broken by the lowest tie key.
    """

    name = "mmr"

    def __init__(self, cfg: SimConfig, n_items: int) -> None:
        super().__init__(cfg, n_items)
        self.lam = cfg.lambda_mmr

    def rank(self, pool, pool_emb, tie_keys):
        U, C = tie_keys.shape
        rel = self.scores(pool_emb)
        sim = np.einsum("uck,udk->ucd", pool_emb, pool_emb)
        chosen = np.zeros((U, C), dtype=bool)
        max_sim = np.full((U, C), 0.0)
        out = np.empty((U, self.k), dtype=np.int64)
        rows = np.arange(U)
        for j in range(self.k):
            score = self.lam * rel - (1.0 - self.lam) * max_sim if j > 0 else self.lam * rel
            score = np.where(chosen, -np.inf, quantise(score))
            best = score.max(axis=1, keepdims=True)
            cand = (score == best) & ~chosen
            pick = np.argmin(np.where(cand, tie_keys, np.inf), axis=1)
            out[:, j] = pick
            chosen[rows, pick] = True
            max_sim = np.maximum(max_sim, sim[rows, pick, :]) if j > 0 else sim[rows, pick, :]
        return out


class LinUCBRanker:
    """Per-user LinUCB (Li et al. 2010) on item embeddings; reward = observed like.

    score_i = theta_u . x_i + alpha * sqrt(x_i^T A_u^{-1} x_i), A_u = lambda I + sum x x^T,
    b_u = sum reward * x. A_u^{-1} is maintained by Sherman-Morrison updates.
    """

    name = "linucb"

    def __init__(self, cfg: SimConfig, n_items: int) -> None:
        self.k = cfg.slate_size
        self.alpha = cfg.alpha_ucb
        d = cfg.n_topics
        self.A_inv = np.repeat(np.eye(d)[None] / cfg.ridge_lambda, cfg.n_users, axis=0)
        self.b = np.zeros((cfg.n_users, d))

    def scores(self, pool_emb):
        theta = np.einsum("ude,ue->ud", self.A_inv, self.b)
        mean = np.einsum("ucd,ud->uc", pool_emb, theta)
        var = np.einsum("ucd,ude,uce->uc", pool_emb, self.A_inv, pool_emb)
        return mean + self.alpha * np.sqrt(np.maximum(var, 0.0))

    def rank(self, pool, pool_emb, tie_keys):
        return order_by_score(self.scores(pool_emb), tie_keys, self.k)

    def update(self, slate, slate_emb, examined, observed_like):
        for j in range(slate_emb.shape[1]):
            m = examined[:, j]
            if not np.any(m):
                continue
            x = slate_emb[m, j, :]
            Ai = self.A_inv[m]
            Ax = np.einsum("ude,ue->ud", Ai, x)
            denom = 1.0 + np.einsum("ud,ud->u", x, Ax)
            self.A_inv[m] = Ai - np.einsum("ud,ue->ude", Ax, Ax) / denom[:, None, None]
            self.b[m] += observed_like[m, j][:, None] * x


REGISTRY = {
    "random": RandomRanker,
    "popularity": PopularityRanker,
    "similarity": SimilarityRanker,
    "linucb": LinUCBRanker,
    "mmr": MMRRanker,
}


def make_ranker(cfg: SimConfig) -> Ranker:
    try:
        cls = REGISTRY[cfg.ranker]
    except KeyError as exc:
        raise ValueError(f"unknown ranker {cfg.ranker!r}") from exc
    return cls(cfg, cfg.n_items)
