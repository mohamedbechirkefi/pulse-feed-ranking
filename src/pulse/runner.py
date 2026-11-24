# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Experiment runner: expands an experiment config into runs, executes them and writes results.

Confirmatory configs are refused unless the protocol is frozen (G-FREEZE): the registry row
must carry a 64-hex SHA-256 that matches the experiment protocol file byte for byte, its
status must no longer say "draft", and research/protocol.md must not be marked DRAFT.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import ConfigError, SimConfig, from_dict, hash_dict
from .manifest import REPO_ROOT, environment, run_manifest
from .schema import DESCRIPTION, SCHEMA_ID, SCHEMA_VERSION, dump_result
from .simulate import simulate


class ProtocolNotFrozen(RuntimeError):
    pass


@dataclass(frozen=True)
class RunSpec:
    experiment_id: str
    label: str
    block: str
    cell: dict
    arm: str
    seed: int
    config: SimConfig

    @property
    def run_id(self) -> str:
        cell = "_".join(f"{k}={v}" for k, v in self.cell.items()) or "base"
        return f"{self.experiment_id}-{self.block}-{cell}-{self.arm}-s{self.seed}"


def load_experiment(path: Path) -> dict:
    exp = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("experiment_id", "label", "output_dir", "base", "seeds", "blocks"):
        if key not in exp:
            raise ConfigError(f"experiment config {path} lacks {key!r}")
    if exp["label"] not in ("exploratory", "confirmatory"):
        raise ConfigError("label must be exploratory or confirmatory")
    out = exp["output_dir"]
    if exp["label"] == "exploratory" and not out.startswith("results/exploratory/"):
        raise ConfigError("exploratory output must live under results/exploratory/")
    if exp["label"] == "confirmatory" and out.startswith("results/exploratory/"):
        raise ConfigError("confirmatory output must not live under results/exploratory/")
    return exp


def expand(exp: dict) -> list[RunSpec]:
    seeds = [exp["seeds"]["first"] + i for i in range(exp["seeds"]["count"])]
    specs: list[RunSpec] = []
    for block in exp["blocks"]:
        factors: dict[str, list] = block.get("factors", {})
        names = list(factors)
        for values in itertools.product(*(factors[n] for n in names)) if names else [()]:
            cell = dict(zip(names, values))
            for arm in block["arms"]:
                arm = dict(arm)
                arm_name = arm.pop("arm")
                cfg = from_dict({**exp["base"], **block.get("overrides", {}), **cell, **arm})
                for s in seeds:
                    specs.append(RunSpec(exp["experiment_id"], exp["label"], block["name"], cell, arm_name, s, cfg))
    ids = [s.run_id for s in specs]
    if len(ids) != len(set(ids)):
        raise ConfigError("experiment expands to duplicate run ids")
    return specs


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def protocol_frozen(experiment_id: str, root: Path = REPO_ROOT) -> tuple[bool, str]:
    main = root / "research" / "protocol.md"
    if not main.exists() or "Status: DRAFT" in main.read_text(encoding="utf-8"):
        return False, "research/protocol.md is marked DRAFT"
    reg = root / "research" / "experiment_registry.csv"
    with reg.open(newline="", encoding="utf-8") as fh:
        rows = {r["exp_id"]: r for r in csv.DictReader(fh)}
    row = rows.get(experiment_id)
    if row is None:
        return False, f"{experiment_id} is not registered"
    h = row.get("protocol_hash", "")
    if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
        return False, f"{experiment_id} has no frozen protocol hash in the registry"
    if "draft" in row.get("status", "").lower():
        return False, f"{experiment_id} registry status is still a draft"
    actual = sha256_file(root / row["protocol_path"])
    if actual != h:
        return False, f"{experiment_id} protocol file hash {actual} does not match the registry"
    return True, "frozen"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def execute(exp: dict, root: Path = REPO_ROOT, out_dir: Path | None = None,
            simulate_fn: Callable[[SimConfig, int], dict] = simulate,
            progress: Callable[[str], None] | None = None) -> Path:
    """Run every spec, write one validated JSON per run plus a set manifest. Returns the output dir."""
    if exp["label"] == "confirmatory":
        ok, why = protocol_frozen(exp["experiment_id"], root)
        if not ok:
            raise ProtocolNotFrozen(f"refusing confirmatory run of {exp['experiment_id']}: {why}")
    out = Path(out_dir) if out_dir is not None else root / exp["output_dir"]
    if (out / "runs").exists() and any((out / "runs").iterdir()):
        raise FileExistsError(f"{out} already holds results; never overwrite raw results")
    specs = expand(exp)
    (out / "runs").mkdir(parents=True, exist_ok=True)
    (out / "result_schema.json").write_text(json.dumps(DESCRIPTION, indent=1) + "\n", encoding="utf-8")
    started = _now()
    t0 = time.perf_counter()
    n_failed = 0
    for i, spec in enumerate(specs):
        run_start = _now()
        t1 = time.perf_counter()
        try:
            res = simulate_fn(spec.config, spec.seed)
            status, error = "ok", None
        except Exception as exc:  # recorded, never dropped (protocol section 8)
            res = {"metrics": {}, "diagnostics": {}}
            status, error = "failed", f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=3)}"
            n_failed += 1
        dt = time.perf_counter() - t1
        record: dict[str, Any] = {
            "schema": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "label": spec.label,
            "experiment_id": spec.experiment_id,
            "run_id": spec.run_id,
            "block": spec.block,
            "cell": spec.cell,
            "arm": spec.arm,
            "seed": spec.seed,
            "config": spec.config.to_dict(),
            "config_hash": spec.config.config_hash(),
            "status": status,
            "error": error,
            "metrics": res["metrics"],
            "diagnostics": res["diagnostics"],
            "manifest": run_manifest(spec.config.config_hash(), spec.seed, run_start, round(dt, 4)),
        }
        dump_result(record, out / "runs" / f"{spec.run_id}.json")
        if progress:
            progress(f"[{i + 1}/{len(specs)}] {spec.run_id} {status} {dt:.2f}s")
    set_manifest = {
        "experiment_id": exp["experiment_id"],
        "label": exp["label"],
        "experiment_config_hash": hash_dict(exp),
        "experiment_config": exp,
        "n_runs": len(specs),
        "n_failed": n_failed,
        "started_utc": started,
        "finished_utc": _now(),
        "wall_clock_s": round(time.perf_counter() - t0, 3),
        "environment": environment(),
    }
    (out / "set_manifest.json").write_text(json.dumps(set_manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out
