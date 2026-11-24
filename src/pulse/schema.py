# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Versioned JSON result schema, validated at export and at import (fail closed).

A small declarative validator is used instead of a JSON Schema library to keep dependencies
minimal. The machine-readable description is written next to results as result_schema.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

SCHEMA_ID = "pulse.run_result"
SCHEMA_VERSION = "1.0.0"
LABELS = ("exploratory", "confirmatory")
STATUSES = ("ok", "failed")
METRICS = ("h_exp", "gini_exposure", "relevance", "miscalibration_kl", "user_control", "like_rate", "delta_h_pref")
BOUNDS = {
    "h_exp": (0.0, 1.0),
    "gini_exposure": (0.0, 1.0),
    "relevance": (0.0, 1.0),
    "miscalibration_kl": (0.0, math.inf),
    "user_control": (-1.0, 1.0),
    "like_rate": (0.0, 1.0),
    "delta_h_pref": (-1.0, 1.0),
}
TOL = 1e-9

DESCRIPTION = {
    "schema": SCHEMA_ID,
    "version": SCHEMA_VERSION,
    "required": {
        "schema": "string, equal to " + SCHEMA_ID,
        "schema_version": "string, equal to " + SCHEMA_VERSION,
        "label": f"one of {list(LABELS)}",
        "experiment_id": "string",
        "run_id": "string, unique within the result set",
        "cell": "object of factor name to value",
        "arm": "string",
        "seed": "non-negative integer (master seed)",
        "config": "object (pulse.config.SimConfig fields)",
        "config_hash": "64-character hex SHA-256 of the canonical config JSON",
        "status": f"one of {list(STATUSES)}",
        "error": "null when status is ok, otherwise a string",
        "metrics": {m: f"number in {list(BOUNDS[m])} or null" for m in METRICS},
        "diagnostics": "object of numbers",
        "manifest": "object (run manifest: git revision, versions, platform, runtime, peak memory)",
    },
}


class SchemaError(ValueError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaError(msg)


def _is_hex64(s: Any) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(ch in "0123456789abcdef" for ch in s)


def validate_result(r: Any) -> None:
    _check(isinstance(r, dict), "result must be an object")
    for key in DESCRIPTION["required"]:
        _check(key in r, f"missing key {key!r}")
    _check(r["schema"] == SCHEMA_ID, "wrong schema id")
    _check(r["schema_version"] == SCHEMA_VERSION, f"unsupported schema_version {r['schema_version']!r}")
    _check(r["label"] in LABELS, "label must be exploratory or confirmatory")
    for key in ("experiment_id", "run_id", "arm"):
        _check(isinstance(r[key], str) and r[key] != "", f"{key} must be a non-empty string")
    _check(isinstance(r["seed"], int) and not isinstance(r["seed"], bool) and r["seed"] >= 0, "seed must be int >= 0")
    _check(isinstance(r["cell"], dict), "cell must be an object")
    _check(isinstance(r["config"], dict), "config must be an object")
    _check(_is_hex64(r["config_hash"]), "config_hash must be a 64-char hex sha256")
    _check(r["status"] in STATUSES, "bad status")
    _check(isinstance(r["manifest"], dict), "manifest must be an object")
    _check(isinstance(r["diagnostics"], dict), "diagnostics must be an object")
    m = r["metrics"]
    _check(isinstance(m, dict), "metrics must be an object")
    if r["status"] == "ok":
        _check(r["error"] is None, "error must be null when status is ok")
        _check(set(m) == set(METRICS), f"metrics keys must be exactly {METRICS}")
        for name in METRICS:
            v = m[name]
            if v is None:
                continue
            _check(isinstance(v, (int, float)) and not isinstance(v, bool), f"metric {name} must be a number")
            _check(math.isfinite(v), f"metric {name} must be finite")
            lo, hi = BOUNDS[name]
            _check(lo - TOL <= v <= hi + TOL, f"metric {name}={v} outside [{lo}, {hi}]")
        _check(m["h_exp"] is not None, "h_exp is required for an ok run")
    else:
        _check(isinstance(r["error"], str) and r["error"], "failed run needs an error message")


def dump_result(r: dict, path: Path) -> None:
    validate_result(r)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(r, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def load_result(path: Path) -> dict:
    r = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_result(r)
    return r


def load_results(directory: Path) -> list[dict]:
    files = sorted(Path(directory).glob("runs/*.json"))
    if not files:
        raise SchemaError(f"no result files under {directory}/runs")
    out = [load_result(f) for f in files]
    ids = [r["run_id"] for r in out]
    _check(len(ids) == len(set(ids)), "duplicate run_id in result set")
    return out
