# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Simulation configuration: typed, validated, hashable.

Units: all sizes are counts; probabilities, rates and weights are dimensionless.
Parameter names follow research/protocol.md section 2.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, fields, replace
from typing import Any

RANKERS = ("random", "popularity", "similarity", "linucb", "mmr")
PREFERENCE_MODELS = ("static", "drifting")
DRIFT_FORMS = ("convex", "additive_clip")
POOL_SKEWS = ("uniform", "zipf")


class ConfigError(ValueError):
    """Raised when a configuration value is missing, of the wrong type or out of range."""


@dataclass(frozen=True)
class SimConfig:
    """One simulation cell plus one ranking arm. The master seed is not part of the config."""

    ranker: str = "random"
    n_users: int = 200  # U
    n_items: int = 1000  # N
    n_topics: int = 10  # K (= embedding dimension d)
    pool_size: int = 50  # C
    slate_size: int = 10  # k
    n_steps: int = 200  # T
    window: int = 50  # W, final metric window in steps
    item_signal: float = 1.0  # a
    item_noise: float = 0.3  # sigma_item
    alpha0: float = 1.0  # Dirichlet concentration of initial preferences
    beta: float = 0.85  # examination decay per position
    tau: float = 0.1  # choice-curve temperature
    eta: float = 0.0  # feedback flip probability
    preference_model: str = "static"
    gamma: float = 0.0  # drift rate (drifting model only)
    drift_form: str = "convex"
    pool_skew: str = "uniform"
    zipf_s: float = 1.0
    alpha_ucb: float = 1.0
    ridge_lambda: float = 1.0
    lambda_mmr: float = 0.5
    calib_alpha: float = 0.01  # Steck 2018 smoothing weight

    def __post_init__(self) -> None:
        validate(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def config_hash(self) -> str:
        return hash_dict(self.to_dict())

    def with_overrides(self, **kw: Any) -> "SimConfig":
        return replace(self, **kw)


def hash_dict(d: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON encoding (sorted keys, no whitespace)."""
    blob = json.dumps(d, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _req(cond: bool, msg: str) -> None:
    if not cond:
        raise ConfigError(msg)


def validate(c: SimConfig) -> None:
    ints = ("n_users", "n_items", "n_topics", "pool_size", "slate_size", "n_steps", "window")
    for name in ints:
        v = getattr(c, name)
        _req(isinstance(v, int) and not isinstance(v, bool), f"{name} must be an int, got {v!r}")
        _req(v >= 1, f"{name} must be >= 1, got {v}")
    floats = [f.name for f in fields(c) if f.type in ("float", float)]
    for name in floats:
        v = getattr(c, name)
        _req(isinstance(v, (int, float)) and not isinstance(v, bool), f"{name} must be a number, got {v!r}")
        _req(v == v and abs(v) != float("inf"), f"{name} must be finite, got {v}")
    _req(c.ranker in RANKERS, f"ranker must be one of {RANKERS}, got {c.ranker!r}")
    _req(c.preference_model in PREFERENCE_MODELS, f"preference_model must be one of {PREFERENCE_MODELS}")
    _req(c.drift_form in DRIFT_FORMS, f"drift_form must be one of {DRIFT_FORMS}")
    _req(c.pool_skew in POOL_SKEWS, f"pool_skew must be one of {POOL_SKEWS}")
    _req(c.n_topics >= 2, "n_topics must be >= 2 (normalised entropy divides by ln K)")
    _req(c.pool_size <= c.n_items, "pool_size must be <= n_items")
    _req(c.slate_size <= c.pool_size, "slate_size must be <= pool_size")
    _req(c.window <= c.n_steps, "window must be <= n_steps")
    _req(c.item_signal > 0, "item_signal must be > 0")
    _req(c.item_noise >= 0, "item_noise must be >= 0")
    _req(c.alpha0 > 0, "alpha0 must be > 0")
    _req(0 < c.beta <= 1, "beta must be in (0, 1]")
    _req(c.tau > 0, "tau must be > 0")
    _req(0 <= c.eta <= 1, "eta must be in [0, 1]")
    _req(0 <= c.gamma <= 1, "gamma must be in [0, 1]")
    _req(c.zipf_s >= 0, "zipf_s must be >= 0")
    _req(c.alpha_ucb >= 0, "alpha_ucb must be >= 0")
    _req(c.ridge_lambda > 0, "ridge_lambda must be > 0")
    _req(0 <= c.lambda_mmr <= 1, "lambda_mmr must be in [0, 1]")
    _req(0 < c.calib_alpha < 1, "calib_alpha must be in (0, 1)")


def from_dict(d: dict[str, Any]) -> SimConfig:
    known = {f.name for f in fields(SimConfig)}
    unknown = set(d) - known
    if unknown:
        raise ConfigError(f"unknown config keys: {sorted(unknown)}")
    return SimConfig(**d)
